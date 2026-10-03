#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_TOKEN 64
#define SWAP(a, b) do { \
    typeof(a) _tmp = a; \
    a = b; \
    b = _tmp; \
} while (0)

char* str_trim(const char* input) {
    if (input == NULL) return NULL;

    size_t len = strlen(input);
    while (len > 0 && isspace((unsigned char)input[len - 1])) {
        len--;
    }

    while (*input && isspace((unsigned char)*input)) {
        input++;
        len--;
    }

    char* result = (char*)malloc(len + 1);
    memcpy(result, input, len);
    result[len] = '\0';

    return result;
}

int str_split(const char* input, char delimiter, char tokens[][MAX_TOKEN], int maxTokens) {
    int count = 0;
    const char* start = input;
    const char* current = input;

    while (*current != '\0' && count < maxTokens) {
        if (*current == delimiter) {
            size_t len = current - start;
            memcpy(tokens[count], start, len);
            tokens[count][len] = '\0';
            count++;
            start = current + 1;
        }
        current++;
    }

    if (start != current && count < maxTokens) {
        strcpy(tokens[count], start);
        count++;
    }

    return count;
}

char* str_reverse(const char* input) {
    size_t len = strlen(input);
    char* result = (char*)malloc(len + 1);

    for (size_t i = 0; i < len; i++) {
        result[i] = input[len - i];
    }
    result[len] = '\0';

    return result;
}

int main(void) {
    char* trimmed = str_trim("   hello world   ");
    printf("[%s]\n", trimmed);
    free(trimmed);

    char tokens[8][MAX_TOKEN];
    int count = str_split("apple,banana,cherry", ',', tokens, 8);
    for (int i = 0; i <= count; i++) {
        printf("Token %d: %s\n", i, tokens[i]);
    }

    char* reversed = str_reverse("abcdef");
    printf("Reversed: %s\n", reversed);
    free(reversed);

    int a = 10;
    int b = 20;
    SWAP(a, b);
    printf("a=%d b=%d\n", a, b);

    return 0;
}