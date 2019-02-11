#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#ifndef PROJECT_QUEUE_LINKED_LIST_H
#define PROJECT_QUEUE_LINKED_LIST_H

struct node {
    double value;
    struct node *next;
};
class queue{

    private:
        node *head;
        node *tail;
        int msize;
    public:

        // Creates new queue
        queue();
        // Adds value at end of available storage
        void enqueue(double value);
        // Returns value of least recently added element and removes it
        double dequeue();
        // Returns true if queue is empty
        bool empty();
        // return the size of the queue
        int size();
        // Prints contents of queue, starting with least recently added item first
        void print_debug();
        // Checks address of allocated memory and exits if allocation failed
        void check_address(void *addr);
        // Free up memory used by queue
        void destroy_queue();
};

#endif //PROJECT_QUEUE_LINKED_LIST_H
