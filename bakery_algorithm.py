from multiprocessing import Process, Array, Value
import time
import ctypes
import random

"""

The Bakery Algorithm was invented by Leslie Lamport in 1974 (Original paper at https://lamport.azurewebsites.net/pubs/bakery.pdf ).

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

"""

class BakeryLock:
    def __init__(self, n):
        self.n = n
        self.choosing = Array(ctypes.c_bool, [False] * n)  # Shared array of booleans
        self.number = Array(ctypes.c_long, [0] * n)       # Shared array of long integers
        self.state = Array(ctypes.c_char, b'_' * n)  # Shared array for state

    def update_state(self, process_id, new_state):
        self.state[process_id] = new_state.encode()
        
    def lock(self, process_id):
        self.update_state(process_id, 'R')  # R for requesting
        # Step 1: Doorway - Choosing a number
        self.choosing[process_id] = True
        time.sleep(random.uniform(0, 0.1)) # Introducing a delay to simulate non-atomic write
        self.number[process_id] = max(self.number) + 1
        time.sleep(random.uniform(0, 0.1)) # Simulate non-atomic read with delay
        self.choosing[process_id] = False

        # Step 2: Wait for the turn
        for other_id in range(self.n):
            while self.choosing[other_id]:
                pass  # Busy wait
            while self.number[other_id] != 0 and (self.number[other_id], other_id) < (self.number[process_id], process_id):
                pass  # Busy wait
        self.update_state(process_id, 'C')  # C for in critical section            

    def unlock(self, process_id):
        self.update_state(process_id, '_')  # _ for not in critical section        
        self.number[process_id] = 0

def critical_section(shared_counter, process_id):
    # Critical section
    old_value = shared_counter.value
    new_value = old_value + 1
    shared_counter.value = new_value

    # Simulate some work
    print(f"Process {process_id} is working...")
    time.sleep(random.random())
    print(f"Process {process_id} finished working!")

    # Validate no other process has entered the critical section
    assert shared_counter.value == new_value, "Mutual exclusion violated"

def process_function(lock, shared_counter, process_id, iterations):
    for _ in range(iterations):
        lock.lock(process_id)
        print(generate_ascii_art(lock))  # Print ASCII art when entering critical section
        critical_section(shared_counter, process_id)
        lock.unlock(process_id)
        print(generate_ascii_art(lock))  # Print ASCII art when leaving critical section
        time.sleep(0.5)  # Small delay between iterations
        
def generate_ascii_art(lock):
    state_symbols = {b'R': 'Requesting', b'C': 'In Critical Section', b'_': 'Waiting'}
    ascii_art = "\nSystem State:\n"
    for i in range(lock.n):
        ascii_art += f"Process {i}: {state_symbols[lock.state[i]]}\n"
    return ascii_art        

def main():
    num_processes = 5
    iterations_per_process = 10
    lock = BakeryLock(num_processes)
    shared_counter = Value('i', 0)  # Shared integer counter
    processes = []

    for process_id in range(num_processes):
        process = Process(target=process_function, args=(lock, shared_counter, process_id, iterations_per_process))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
        
    print(generate_ascii_art(lock))
    print(f"Final counter value: {shared_counter.value}")
    assert shared_counter.value == num_processes * iterations_per_process, "Final counter value does not match expected"

if __name__ == "__main__":
    main()
