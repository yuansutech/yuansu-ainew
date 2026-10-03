use std::collections::VecDeque;

struct RingBuffer<T> {
    data: VecDeque<T>,
    capacity: usize,
}

impl<T> RingBuffer<T> {
    fn new(capacity: usize) -> Self {
        RingBuffer {
            data: VecDeque::with_capacity(capacity),
            capacity,
        }
    }

    fn push(&mut self, item: T) -> Option<T> {
        let evicted = if self.data.len() == self.capacity {
            self.data.pop_front()
        } else {
            None
        };
        self.data.push_back(item);
        evicted
    }

    fn pop(&mut self) -> Option<T> {
        self.data.pop_front()
    }

    fn len(&self) -> usize {
        self.data.len()
    }

    fn is_full(&self) -> bool {
        self.data.len() == self.capacity
    }
}

fn sum_buffer(buffer: &RingBuffer<i32>) -> i32 {
    let mut total = 0;
    for item in buffer.data.iter() {
        total += *item;
    }
    total
}

fn drain_and_sum(buffer: &mut RingBuffer<i32>) -> i32 {
    let mut total = 0;
    while let Some(value) = buffer.pop() {
        total += value;
    }
    total
}

fn main() {
    let mut buffer = RingBuffer::new(3);

    buffer.push(1);
    buffer.push(2);
    buffer.push(3);
    buffer.push(4);

    println!("Length: {}", buffer.len());
    println!("Is full: {}", buffer.is_full());
    println!("Sum: {}", sum_buffer(&buffer));

    let total = drain_and_sum(&mut buffer);
    println!("Drained sum: {}", total);
    println!("Length after drain: {}", buffer.len());

    let reference = &buffer;
    drop(buffer);

    println!("Still here: {:?}", reference.len());
}