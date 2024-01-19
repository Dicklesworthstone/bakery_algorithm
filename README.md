# Lamport's Bakery Algorithm Demonstrated in Python

The Bakery Algorithm was invented by Leslie Lamport in 1974 (Original paper at [https://lamport.azurewebsites.net/pubs/bakery.pdf] ).

It is a locking mechanism used in concurrent programming to prevent multiple processes from entering their critical sections simultaneously, which could cause data corruption or inconsistencies. It's named after the numbering system used in bakeries, where each customer gets a number and waits for their turn to be served.

Here’s how it works:

    * Number Assignment: Each process that wants to enter the critical section takes a number. This number is usually one greater than the maximum number currently in use by any process. This ensures a unique and sequentially increasing number for each process.

    * Waiting for Turn: A process must wait until it's its turn to enter the critical section. The order is determined by the numbers - lower numbers go first. If two processes have the same number (which is theoretically possible due to race conditions in the number assignment step), the process with the lower process ID goes first.

    * Entering Critical Section: Once it's a process's turn (no other process has a lower number, or those with lower numbers are not interested in entering the critical section), the process enters the critical section.

    * Exiting Critical Section: After the process exits the critical section, it relinquishes its number, allowing other processes to proceed.

This algorithm ensures mutual exclusion, meaning no two processes can be in their critical sections simultaneously.

The key advantage of the Bakery Algorithm is its fairness - every process gets a chance to enter its critical section in a finite amount of time, preventing starvation. However, it can be inefficient if there are many processes, as the waiting process must continuously check if it's its turn, leading to busy-waiting.

The Bakery Algorithm's unique feature is its ability to ensure mutual exclusion in concurrent programming without requiring atomic reads and writes. This makes it powerful, especially in systems where atomicity cannot be guaranteed due to hardware limitations or other constraints.

In most synchronization algorithms, ensuring mutual exclusion typically requires operations (like updating flags, counters, or other variables) to be atomic. Atomic operations are indivisible and uninterruptible, ensuring that no other process can see their intermediate states. This is crucial in preventing race conditions where multiple processes access and modify shared data concurrently, leading to inconsistent or erroneous states.

However, the Bakery Algorithm is designed to work even when reads and writes to shared variables are not atomic. It achieves this through its clever numbering system:

    * Non-atomic Number Assignment: When a process wants to enter the critical section, it assigns itself a number. This number is based on the highest number currently in use, incremented by one. Even if this read and write are not atomic, the system still works. If two processes read the same "highest number" simultaneously due to non-atomicity, they will end up with the same number. The algorithm resolves this tie by using the process IDs, which are unique.

    * Ordering by Numbers and IDs: Each process checks the numbers of all other processes to determine if it's its turn. If two processes have the same number, the tie is broken by process ID. This step tolerates non-atomic reads because, even if a process reads an outdated number, it only leads to a delay in entering the critical section, not a violation of mutual exclusion.

    * Tolerating Inconsistent Views: Since the algorithm doesn't rely on atomicity, different processes may have inconsistent views of the shared state (like the numbers assigned to each process). However, the algorithm is designed such that these inconsistencies don't lead to mutual exclusion violations. They might only cause a process to wait longer than necessary.

The following Python code attempts to demonstrate how this algorithm works. This is somewhat challenging given Python's Global Interpreter Lock (GIL), which prevents true parallelism. However, we can still simulate the algorithm's behavior by introducing delays in the code and by using multiple processes.
