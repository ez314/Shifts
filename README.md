# Shift Scheduler

## Running instructions

Developed using Python 3.10
```bash
python main.py
```

## Problem

There are N time units. For each of the N units, there are X[N] availabilities.  

A shift consists of M consecutive time units within the N units. It takes up 1
availability from each time unit it covers. A shift cannot exist if there are 
no availabilities.

For example:

> N = 5  
> M = 3  
> X[N] = [2, 1, 1, 0, 1]  
> 
> | time                                | 1   | 2   | 3   | 4   | 5   |
> |-------------------------------------|-----|-----|-----|-----|-----|
> | availability                        | 2   | 1   | 1   | 0   | 1   |
> | shift 1                             | 1   | 1   | 1   |     |     |
> | shift 2                             |     |     | 1   | 1   | 1   |
> | availability after removing shift 1 | 1   | 0   | 0   | 0   | 1   |
> 
> Shift 1 is valid because time units 1, 2, and 3 have availability.  
> Shift 2 is invalid because time unit 4 does not have availability.
> 
> After removing shift 1 from the availability, X[N] decreases by 1 where it
> overlapped wth shift 1.

How many equal-sized shifts can you remove, given some availability?


## General Recursive Algorithm (DFS)

The problem can be solved recursively. Suppose a fairy told you they could solve
this problem for you, as long as you removed one shift from the availabilities. 
Then, you would go through the entire list and try to remove a shift from every 
starting point. After removing each shift, you'd ask the fairy to solve the 
remaining subproblem. Your final solution is the _best subproblem solution_(based on 
what the fairy tells you) _+ 1_ (the shift you just removed).  

It's easy to determine if no shifts can be removed given some availability. Just
scan the whole list. If there isn't a block of M consecutive time units with 
availability in all N time units, then the answer is 0. So when the solution is 0,
you don't need the fairy.

Now, say the solution to some problem is S. At every step, you remove one shift from
the availability. The solution to this subproblem is at most S-1. Instead of passing
it to the fairy, you remove one more shift from the subproblem. At this stage, the 
solution is at most S-2. After up to S steps, you've reached the case above, and you
no longer need the fairy at all. You've become your own fairy.

One algorithm for the above might look like this:
```
DEFINE SOLVE(availability):
    CALCULATE valid_shifts FROM availability
    
    solution = 0
    
    FOR shift IN valid_shifts:
        subproblem_availabiity = REMOVE shift FROM availability 
        subproblem_solution = SOLVE(subproblem_availability)
        IF subproblem_solution + 1 > solution:
            solution = subproblem_solution + 1
           
    RETURN solution
```

Every time `SOLVE` is called, a shift is removed. Eventually, after many calls, 
`valid_shifts` will be empty and `SOLVE` returns 0 without looping.

This solution is extremely slow, because it tries every possible shift at every
possible stage. This is worse than brute-force. It's also solving the same subproblem
multiple times without knowing it. 

Say the availability is [1, 1, 0, 1, 1] and the shift length M is 2. 

- The first call to `SOLVE` might remove the first possible shift (t=1,2). 
  - The second call gets [0, 0, 0, 1, 1] as input and removes t=4,5 since that is the 
  only valid shift. 
    - The third call gets [0, 0, 0, 0, 0] as input, finds no valid shifts, and 
    returns 0.
- The first call to `SOLVE` then tries to remove the second possible shift (t=4,5).
  - The second call gets [1, 1, 0, 0, 0] as input and removes t=1,2 since that is the
  only valid shift.
    - The third call gets [0, 0, 0, 0, 0] as input, finds no valid shifts, and 
    returns 0.

The third call in both cases gets passed the same input. The algorithm scans through
[0, 0, 0, 0, 0] twice. This issue of repeated work becomes much worse with more
time units (larger N) and more availability per time unit (larger X[i] for i in N). 

If we go back to the example, we see that the problem comes from some deficiencies:
1. Since each call scans through the entire availability list, each call is
capable of removing a shift from anywhere in that list
2. 2 calls in the same call chain might "swap" shifts, if this happens, the same
availability list will be generated twice, and the remainder of the call tree will
be a duplicate.

## Another Recursive Algorithm (DFS)

Luckily, it's pretty easy to prune the call tree. At each call, only consider the 
first valid shift. Determine the number of overlapping shifts that can fit in the
same block of time. That number is the min availability over that block of time. 
Say the number is A.

In the best solution, a shift must occur at this block of time between 0 and A 
times. It cannot be less than 0, and it cannot be more than A.

> Example  
> 
> | time         | 1   | 2   | 3   | 4   | 5   |
> |--------------|-----|-----|-----|-----|-----|
> | availability | 3   | 3   | 4   | 4   | 3   |
> | shift        | 1   | 1   | 1   |     |     |
> 
> In this case, the min availability in time1,2,3 is 3. Up to 3 total shifts may
> occur at the block of time taken by this shift.

Now, at each stage, take between 0 and A shifts out of the availability, and lock 
this block of time from future calls. The easy way to do this is to instruct future
calls to start looking for available shifts after the start time of this shift.

Here is the modified algorithm:
```
DEFINE SOLVE(availability, search_start=1):
    CALCULATE first_valid_shift FROM availability STARTING AT search_start
    
    IF first_valid_shift DOES NOT EXIST:
        RETURN 0
    
    min_availability = MIN availability ACROSS first_valid_shift
    
    solution = 0
    FOR n IN RANGE (0 TO min_availability) INCLUSIVE:
        subproblem_availabiity = REMOVE n * first_valid_shift FROM availability
        subproblem_solution = SOLVE(subproblem_availability, first_valid_shift.start + 1)
        IF subproblem_solution + 1 > solution:
            solution = subproblem_solution + 1
           
    RETURN solution
```

However, this solution is still very slow. Even though we've stopped exploring the 
same possibilities multiple times, we still explore every possibility once. 

This comes from the following deficiency: It's very unlikely for the solution to be
when `n` is close to `0`, since that is locally sub-optimal. In other words, if
there was a solution where `n` was `0`, those `n` shifts you just skipped over must 
be replaced with `n` other shifts in a later call to `SOLVE`. 

In fact, one call chain will always be to remove `0` shifts at every call. It is
unnecessary to explore this solution. In some ways, this algorithm is just as bad.
We've traded off doing repeated work for doing unnecessary work.

## Fast Algorithm (Greedy)

But, it turns out that the previous algorithm works when you always remove
`min_availability` shifts. That is, given any availability, always remove the
first shift as many times as you can.

```
DEFINE SOLVE(availability, search_start=1):
    CALCULATE first_valid_shift FROM availability STARTING AT search_start
    
    IF first_valid_shift DOES NOT EXIST:
        RETURN 0
    
    min_availability = MIN availability ACROSS first_valid_shift
    
    n = min_availability

    subproblem_availabiity = REMOVE n * first_valid_shift FROM availability
    subproblem_solution = SOLVE(subproblem_availability, first_valid_shift.start + 1)
    solution = subproblem_solution + 1
           
    RETURN solution
```

We can do a proof by contradiction to show this is correct.

[x,y] means a shift starting at x and ending at y. 

This algorithm asserts that given any availability, the first valid shift [a,b] is 
always the first shift in the solution. Suppose someone says the first shift in the
solution is not [a,b], and instead it is [c,d] where c>a. 

There are 2 cases:
1. [a,b] is still a valid shift after removing [c,d]. For example, if
[a.b] and [c,d] don't overlap at all (b < c).
2. [a,b] is not a valid shift after removing [c,d]. For example, if [a,b] and [c,d]
overlap (b >= c). 

In this first case, the other person is wrong. Choosing [c,d] does not eliminate 
[a,b] as a valid shift. So we can add [a.b] to their answer and make it better.

In the second case, the other person may have the correct solution, but the solution
with [a,b] is just as good. This is because the other person can replace
[c,d] with [a,b] and still have a valid solution with the same number of shifts.

So, in any case, choosing the first valid shift is optimal. 