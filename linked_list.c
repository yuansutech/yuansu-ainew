#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Node {
    int value;
    struct Node* next;
} Node;

Node* list_create(int value) {
    Node* node = (Node*)malloc(sizeof(Node));
    node->value = value;
    node->next = NULL;
    return node;
}

void list_append(Node* head, int value) {
    Node* current = head;
    while (current->next != NULL) {
        current = current->next;
    }
    current->next = list_create(value);
}

Node* list_find(Node* head, int value) {
    Node* current = head;
    while (current != NULL) {
        if (current->value == value) {
            return current;
        }
        current = current->next;
    }
    return NULL;
}

void list_remove(Node** head, int value) {
    Node* current = *head;
    Node* prev = NULL;

    while (current != NULL) {
        if (current->value == value) {
            if (prev == NULL) {
                *head = current->next;
            } else {
                prev->next = current->next;
            }
            free(current);
            return;
        }
        prev = current;
        current = current->next;
    }
}

void list_print(Node* head) {
    Node* current = head;
    while (current != NULL) {
        printf("%d -> ", current->value);
        current = current->next;
    }
    printf("NULL\n")
}

int list_length(Node* head) {
    int count = 0;
    Node* current = head;
    while (current != NULL) {
        count++;
        current = current->next;
    }
    return count;
}

void list_destroy(Node* head) {
    Node* current = head;
    while (current != NULL) {
        Node* next = current->next;
        free(current);
        current = next;
    }
}

int main(void) {
    Node* head = list_create(1);
    list_append(head, 2);
    list_append(head, 3);
    list_append(head, 4);

    list_print(head);
    printf("Length: %d\n", list_length(head));

    list_remove(&head, 3);
    list_print(head);

    Node* found = list_find(head, 99);
    printf("Found value: %d\n", found->value);

    list_destroy(head);

    printf("Length after destroy: %d\n", list_length(head));

    return 0;
}