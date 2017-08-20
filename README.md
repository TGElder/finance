This is a simple tool to allow managing personal finances when:

* You have one or many real bank accounts
* You have a number of virtual accounts (e.g. part of your savings may be ring fenced for holidays)
* You want to track 'commitments' (e.g. you may be expecting to pay the balance on a holiday and want to make sure you don't accidentally spend that money)

# CSV Files #

The tool is backed by four CSV files. See the **test** folder for examples. Note that amounts are always in whole numbers (e.g. pennies instead of pounds).

## readings.csv ##

Use this to track the actual balance of your accounts, e.g.

id|Account|Reading|Date
---|---|---|---
1|Personal|100000|21-05-17
2|Savings|1000000|21-05-17

The system will always use the last reading (highest id) for each account.

## transfers.csv ##

Use this to transfer money in and out of your virtual accounts. For example, I might initially add a transfer to note that some of my savings are allocated to my holiday fund:

id|From|To|What|Amount|Added
---|---|---|---|---|---
1|Savings|Holidays|Init|100000|23-07-17

Since I don't have an actual account for my holiday fund, I may end up paying for it with my personal account. I can add a transaction to balance this:

id|From|To|What|Amount|Added
---|---|---|---|---|---
1|Holidays|Personal|Holiday Payment|20000|11-08-17

## commitments.csv ##

Use this to mark transfers that may happen in the future, e.g. money someone owes you:

id|From|To|What|Amount|Added
---|---|---|---|---|---
1|Outside|Personal|Money Owed by Dave|8000|12-08-17

Or emergency funds you don't want to spend:

id|From|To|What|Amount|Added
---|---|---|---|---|---
2|Savings|Outside|Emergency Fund|500000|21-05-17

The only difference between commitments and transfers is that commitments can be closed by adding a line to **close_dates.csv**. For example, once Dave pays me back I can close the commitment so it is not counted twice.

# Usage #

Create a finance object

```
import finance
finance = finance.Finance("database")
```

The string used to create the object should be a directory containing the four CSV files above.

Use `finance.print_summary()` to get a human readable summary of the balance in each of your accounts. The balance is the latest reading for each account + any transfers in + any commitments.

Use `finance.create_transfers_from_table(table,prefix)` to create transfers from another table (i.e. another CSV file). The **test** folder contains an example **monthly_budgets.csv**. The optional prefix is appended to the What column for the resulting transfers. This is a convinient way of adding a lot of transactions at once, or for adding the same transactions repeatedly (e.g. monthly budgets).

`finance.set_transfer_to_zero(account,using)` will
* Create a transfer between the two specified accounts (`account` and `using`) so that the total transfers to `account` is zero.
* Add new readings for both accounts so the balance of each account remain unchanged.
* Print an instruction (e.g. "Transfer 150 from Savings to Personal"). This is important - since readings are supposed to reflect balances of real bank accounts, a real transfer must be made between them.

`set_transfer_to_zero` is used to get the real balance of `account` as close to its actual balance as possible (i.e. as close as possible excluding commitments).

# Tests #

Run `python -m pytest` to test the system.