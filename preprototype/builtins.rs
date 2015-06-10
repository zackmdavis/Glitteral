use std::io;
use std::fmt::Display;
use std::collections::HashMap;

// Glitteral standard library arithmetic
fn integers_equal(a: isize, b: isize) -> bool { a == b }
fn integers_not_equal(a: isize, b: isize) -> bool { a != b }
fn add_integers(a: isize, b: isize) -> isize { a + b }
fn subtract_integers(a: isize, b: isize) -> isize { a - b }
fn multiply_integers(a: isize, b: isize) -> isize { a * b }
fn divide_integers(a: isize, b: isize) -> isize { a / b }
fn greater(a: isize, b: isize) -> bool { a > b }
fn less(a: isize, b: isize) -> bool { a < b }
fn not_less(a: isize, b: isize) -> bool { a >= b }
fn not_greater(a: isize, b: isize) -> bool { a <= b }

// more builtins
fn append(list: &mut Vec<isize>, item: isize) -> &mut Vec<isize> {
    list.push(item);
    list
}
fn length<T>(container: &Vec<T>) -> isize {
    container.len() as isize
}
fn range(start: isize, end: isize) -> Vec<isize> {
    let mut items = vec![];
    for i in start..end {
        items.push(i)
    }
    items
}

// special
fn list_get_subscript(container: &mut Vec<isize>, index: isize) -> isize {
    container[index as usize]
}

// fn dictionary_get_subscript<K: Eq + Hash + Clone, V>(container: &mut HashMap<K, V>, key: &K) -> V {
//     *container.get(&key).unwrap().clone()
// }
//
// XXX TODO FIXME: we would really prefer to use a generic hashmap rather than
// artificially constrain the types of Glitteral associatives or repeat the same
// function with different types several times, but have temporarily tired of
// beating our fists against the iron wall of "`cannot move out of borrowed
// content`"
fn str_int_dictionary_get_subscript(container: &mut HashMap<&str, isize>, key: &str) -> isize {
    *container.get(key).unwrap()
}

// conjunction and disjunction
fn and(a: bool, b: bool) -> bool {
    a && b
}
fn or(a: bool, b: bool) -> bool {
    a || b
}

// Glitteral standard library IO
fn print_integer(n: isize) { println!("{}", n); }
fn println_container(l: &mut Vec<isize>) { println!("{:?}", l); }
fn print<T: Display>(printable: T) { print!("{}", printable); }
fn println<T: Display>(printable: T) { println!("{}", printable); }
fn input() -> String {
    let mut input_buffer = String::new();
    io::stdin()
        .read_line(&mut input_buffer)
        .ok().expect("Glitteral IO failure");
    input_buffer.trim().to_string()
}
