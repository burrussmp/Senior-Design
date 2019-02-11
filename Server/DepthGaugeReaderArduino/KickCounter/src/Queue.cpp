#include "queue.h"
queue::queue(): head(nullptr),tail(nullptr),msize(0) {
}

void queue::enqueue(double value) {
  struct node *new_node = (struct node *)(malloc(sizeof(struct node)));
  check_address(new_node);

  new_node->value = value;
  new_node->next = 0;

  if (tail) {
    tail->next = new_node;
  }
  tail = new_node;

  if (head == 0) {
    head = new_node;
  }
  msize = msize + 1;
}

double queue::dequeue() {

  if (empty()) {
    printf("Unable to dequeue. Queue is empty.\n");
    exit(EXIT_FAILURE);
  }

  double value = head->value;

  node *temp = head;

  if (tail == head) {
    tail = nullptr;
  }

  head = head->next;
  free(temp);
  msize = msize -1;
  return value;
}

bool queue::empty() {
  return head == nullptr;
}

int queue::size(){
    return msize;
}

void queue::print_debug() {
  printf("Queue contents: ");

  struct node *current = head;

  while (current) {
    printf("%0.2f < ", current->value);
    current = current->next;
  }

  printf("\n");
}

void queue::check_address(void *addr) {
  if (addr == 0) {
    printf("Unable to allocate more memory.\n");
    exit(EXIT_FAILURE);
  }
}

void queue::destroy_queue() {

  struct node *current = head;
  struct node *temp = head;

  while (current) {
    temp = current;
    current = current->next;
    delete temp;
  }

}