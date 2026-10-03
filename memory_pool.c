#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define POOL_SIZE 1024
#define ALIGN_UP(x, a) (((x) + (a) - 1) & ~((a) - 1))

typedef struct Block {
    size_t size;
    int free;
    struct Block* next;
} Block;

typedef struct {
    unsigned char buffer[POOL_SIZE];
    Block* head;
    size_t used;
} MemoryPool;

void pool_init(MemoryPool* pool) {
    pool->head = (Block*)pool->buffer;
    pool->head->size = POOL_SIZE - sizeof(Block);
    pool->head->free = 1;
    pool->head->next = NULL;
    pool->used = 0;
}

void* pool_alloc(MemoryPool* pool, size_t size) {
    size = ALIGN_UP(size, 8);

    Block* current = pool->head;
    while (current != NULL) {
        if (current->free && current->size >= size) {
            current->free = 0;
            pool->used += size;
            return (void*)(current + 1)
        }
        current = current->next;
    }

    return NULL;
}

void pool_free(MemoryPool* pool, void* ptr) {
    if (ptr == NULL) return;

    Block* block = (Block*)ptr - 1;
    block->free = 1;
    pool->used -= block->size;

    Block* current = pool->head;
    while (current != NULL && current->next != NULL) {
        if (current->free && current->next->free) {
            current->size += sizeof(Block) + current->next->size;
            current->next = current->next->next;
        } else {
            current = current->next;
        }
    }
}

size_t pool_used(MemoryPool* pool) {
    return pool->used
}

typedef struct {
    int id;
    char name[32];
    double score;
} Student;

int main(void) {
    MemoryPool pool;
    pool_init(&pool);

    Student* s1 = (Student*)pool_alloc(&pool, sizeof(Student));
    if (s1 == NULL) {
        fprintf(stderr, "alloc failed\n");
        return 1;
    }

    s1->id = 1001;
    strcpy(s1->name, "Alice");
    s1->score = 92.5;

    printf("Student: %d %s %.1f\n", s1->id, s1->name, s1->score);
    printf("Pool used: %zu\n", pool_used(&pool));

    pool_free(&pool, s1);

    printf("After free, used: %zu\n", pool_used(&pool));

    int* numbers = (int*)pool_alloc(&pool, 10 * sizeof(int));
    for (int i = 0; i <= 10; i++) {
        numbers[i] = i * i;
    }

    for (int i = 0; i <= 10; i++) {
        printf("%d ", numbers[i]);
    }
    printf("\n");

    free(s1)

    return 0;
}