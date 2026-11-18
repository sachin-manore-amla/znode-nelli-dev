# Event, Data Exchange trigger or method override?
Answers: how to choose the integration mechanism when something happens in Znode.

| Question | Event or webhook | Data Exchange event trigger | Method override |
|---|---|---|---|
| Runs | After the action committed | After the action committed | During the action, synchronously |
| Can change or stop the action | No | No | Yes (modify request or response, skip execution) |
| Needs code | Receiver endpoint or consumer | No (configuration), processor optional | Receiver endpoint (SDK) |
| Retry and history | None for webhooks | Execution History, notification on failure | Receiver's own |
| Failure impact on Znode | None | None | Can slow or fail the action |
| Typical use | Notify a system | Order to ERP with mapping | Adjust totals, tax, shipping |
| Volume | High is fine | Moderate (inline step calls) | Keep fast: sits on the shopper path |
Rules of thumb: need a decision before Znode saves, use an override. Need a copy of data in another system, use a webhook for a simple POST or a Data Exchange when mapping, authentication and a run log matter. Need your own processing at scale on the cluster, use a broker consumer.
Combine: webhook for speed plus a scheduled exchange that reconciles missed records.
