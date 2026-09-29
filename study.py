"""Rolling distributional forecasts and exact constrained staffing decisions."""
from pathlib import Path
import json
import numpy as np
from common import write_csv,save_summary,ridge_fit,ridge_predict,block_interval

CONFIG=json.loads(Path('config.json').read_text())
METHODS=['buffer_rule','point_plan','stochastic_plan','perfect_information']

def generate(config,scenario):
    rng=np.random.default_rng(config['seed']);values=[];shock=0
    pattern=np.array([-25,0,15,25,35,5,-30])
    for week in range(config['weeks']):
        volatile=scenario=='volatile' and week>=config['test_start_week']
        shock=.6*shock+rng.normal(0,24 if volatile else 12)
        demand=175+.18*week+pattern+18*np.sin(2*np.pi*week/52)+shock+rng.normal(0,20 if volatile else 10,7)
        if scenario=='surge' and week>=config['test_start_week']:demand*=1.2
        values.extend(np.maximum(0,np.rint(demand)).astype(int))
    return np.array(values)

def week_features(history,week):
    assert len(history)>=week*7
    if week<4:raise ValueError('Four past weeks required')
    days=week*7+np.arange(7)
    past=history[(week-4)*7:week*7].reshape(4,7)
    return np.column_stack([np.eye(7)[:,:6],days/364,np.sin(2*np.pi*days/364),np.cos(2*np.pi*days/364),past[-1],past.mean(axis=0),np.full(7,past[-1].mean())])

def forecast(demand,week):
    # Slice once at the information boundary; downstream code cannot see future values.
    history=np.asarray(demand[:week*7])
    start=max(4,week-104)
    x=np.concatenate([week_features(history,w) for w in range(start,week)])
    y=history[start*7:week*7]
    model=ridge_fit(x,y,20)
    return np.round(np.maximum(0,ridge_predict(model,week_features(history,week))),6)

def recourse(demand,workers,config):
    demand=np.atleast_1d(demand);ot=np.arange(config['overtime_max']+1)
    capacity=(workers+ot)*config['units_per_worker']
    unmet=np.maximum(0,demand[:,None]-capacity)
    cost=workers*config['regular_cost']+ot*config['overtime_cost']+unmet*config['shortage_cost']
    choice=cost.argmin(axis=1);idx=np.arange(len(demand))
    return cost[idx,choice],unmet[idx,choice],choice,np.maximum(0,capacity[choice]-demand)

def optimize(costs,minimum,maximum,budget,ramp):
    original_costs=np.asarray(costs,dtype=float)
    # Compare integer micro-dollar costs so algebraically tied schedules do not
    # depend on floating-point summation or linear-algebra platform details.
    costs=np.rint(original_costs*1_000_000)
    days,k=costs.shape
    if k!=maximum-minimum+1 or budget<days*minimum:raise ValueError('Infeasible dimensions or budget')
    workers=np.arange(minimum,maximum+1)
    dp=np.full((budget+1,k),np.inf);backs=np.full((days,budget+1,k),-1,int)
    for j,w in enumerate(workers):
        if w<=budget:dp[w,j]=costs[0,j]
    for day in range(1,days):
        nxt=np.full_like(dp,np.inf)
        for j,w in enumerate(workers):
            lo=max(0,j-ramp);hi=min(k,j+ramp+1)
            choices=dp[:budget+1-w,lo:hi];arg=choices.argmin(axis=1)
            nxt[w:,j]=choices[np.arange(len(arg)),arg]+costs[day,j]
            backs[day,w:,j]=arg+lo
        dp=nxt
    used,last=np.unravel_index(dp.argmin(),dp.shape)
    if not np.isfinite(dp[used,last]):raise ValueError('No feasible plan')
    plan=[]
    for day in range(days-1,-1,-1):
        w=int(workers[last]);plan.append(w);prior=backs[day,used,last];used-=w;last=prior
    plan=np.array(plan[::-1])
    objective=float(sum(original_costs[day,w-minimum] for day,w in enumerate(plan)))
    return plan,objective

def expected_costs(scenarios,config):
    workers=range(config['workers_min'],config['workers_max']+1)
    return np.array([[recourse(scenarios[:,day],w,config)[0].mean() for w in workers] for day in range(scenarios.shape[1])])

def plan_from_costs(costs,config):return optimize(costs,config['workers_min'],config['workers_max'],config['worker_days_budget'],config['max_day_change'])[0]

def realized(demand,plan,config):
    return np.array([[float(v[0]) for v in recourse(np.array([d]),int(w),config)] for d,w in zip(demand,plan)])

def evaluate(config,scenario):
    demand=generate(config,scenario)
    write_csv(f'data/{scenario}_demand.csv',['day','week','weekday','demand'],[[d,d//7,d%7,int(v)] for d,v in enumerate(demand)])
    errors=[];records=[];weekly=[];calibrations=[];sensitivities={penalty:[] for penalty in [12,24,48]}
    workers=np.arange(config['workers_min'],config['workers_max']+1)
    for week in range(26,config['weeks']):
        prediction=forecast(demand,week);actual=demand[week*7:(week+1)*7]
        if week>=config['test_start_week']:
            scenarios=np.maximum(0,prediction+np.array(errors[-52:]))
            lower,upper=np.quantile(scenarios,[.1,.9],axis=0)
            naive=demand[(week-1)*7:week*7]
            target=np.ceil(1.2*naive/config['units_per_worker'])
            plans={'buffer_rule':plan_from_costs((workers[None,:]-target[:,None])**2,config),'point_plan':plan_from_costs(expected_costs(prediction[None,:],config),config),'stochastic_plan':plan_from_costs(expected_costs(scenarios,config),config),'perfect_information':plan_from_costs(expected_costs(actual[None,:],config),config)}
            for method,plan in plans.items():
                outcomes=realized(actual,plan,config)
                weekly.append([week,method,outcomes[:,0].sum(),outcomes[:,1].sum(),outcomes[:,2].sum(),outcomes[:,3].sum(),actual.sum(),plan.sum()])
                for day in range(7):records.append([week,day,method,int(actual[day]),prediction[day],lower[day],upper[day],int(plan[day]),*outcomes[day]])
            for penalty in sensitivities:
                cfg={**config,'shortage_cost':penalty}
                plan=plans['stochastic_plan'] if penalty==config['shortage_cost'] else plan_from_costs(expected_costs(scenarios,cfg),cfg)
                outcomes=realized(actual,plan,cfg)
                sensitivities[penalty].append([outcomes[:,0].sum(),outcomes[:,1].sum(),actual.sum(),plan.sum(),outcomes[:,2].sum()])
            calibrations.append([week,float(np.abs(prediction-actual).sum()),float(np.abs(naive-actual).sum()),float(actual.sum()),float(((actual>=lower)&(actual<=upper)).sum())])
        # Calibration is updated only after this week's decision and outcome evaluation.
        errors.append(actual-prediction)
    write_csv(f'results/{scenario}_daily_decisions.csv',['week','weekday','method','demand','forecast','lower80','upper80','regular_workers','cost','shortage_units','overtime_workers','unused_capacity'],records)
    write_csv(f'results/{scenario}_weekly.csv',['week','method','cost','shortage_units','overtime_worker_days','unused_capacity','demand','regular_worker_days'],weekly)
    aggregate={};baseline=np.array([r[2] for r in weekly if r[1]=='buffer_rule'])
    oracle=np.array([r[2] for r in weekly if r[1]=='perfect_information'])
    for method in METHODS:
        r=np.array([v[2:] for v in weekly if v[1]==method])
        assert np.all(r[:,0]+1e-6>=oracle)
        mean,lo,hi=block_interval(baseline-r[:,0],np.random.default_rng(config['seed']+100),config['bootstrap_draws'])
        aggregate[method]={'total_cost':r[:,0].sum(),'mean_weekly_cost':r[:,0].mean(),'service_rate':1-r[:,1].sum()/r[:,4].sum(),'shortage_units':r[:,1].sum(),'overtime_worker_days':r[:,2].sum(),'unused_capacity':r[:,3].sum(),'regular_worker_days':r[:,5].sum(),'weekly_savings_vs_buffer':mean,'savings_lower95':lo,'savings_upper95':hi,'gap_to_perfect_information':r[:,0].sum()-oracle.sum()}
    c=np.array(calibrations);sensitivity=[]
    for penalty,values in sensitivities.items():
        v=np.array(values);sensitivity.append({'shortage_penalty':penalty,'total_cost':v[:,0].sum(),'service_rate':1-v[:,1].sum()/v[:,2].sum(),'regular_worker_days':v[:,3].sum(),'overtime_worker_days':v[:,4].sum()})
    return {'scenario':scenario,'test_weeks':len(calibrations),'forecast':{'model_wape':c[:,1].sum()/c[:,3].sum(),'naive_wape':c[:,2].sum()/c[:,3].sum(),'coverage80':c[:,4].sum()/(7*len(c))},'policies':aggregate,'cost_sensitivity':sensitivity}

def main():
    summary={'study':'operational-planning','config':CONFIG,'scenarios':[evaluate(CONFIG,s) for s in CONFIG['scenarios']]};save_summary(summary)
    print(json.dumps({s['scenario']:{'forecast':s['forecast'],'policies':s['policies']} for s in summary['scenarios']},default=float,indent=2))

if __name__=='__main__':main()
