use std::io;
use std::fmt::Display;
use std::collections::HashMap;
use std::thread::sleep_ms;
use std::ops::{Add, Sub, Mul, Div};
use std::process::Command;
use std::str::from_utf8;

// Glitteral standard library arithmetic
fn integers_equal(a: isize, b: isize) -> bool { a == b }
fn integers_not_equal(a: isize, b: isize) -> bool { a != b }
fn add<N: Add<Output = N>>(a: N, b: N) -> N { a + b }
fn subtract<N: Sub<Output = N>>(a: N, b: N) -> N { a - b }
fn multiply<N: Mul<Output = N>>(a: N, b: N) -> N { a * b }
fn divide<N: Div<Output = N>>(a: N, b: N) -> N { a / b }
fn greater<T: PartialOrd>(a: T, b: T) -> bool { a > b }
fn less<T: PartialOrd>(a: T, b: T) -> bool { a < b }
fn not_less<T: PartialOrd>(a: T, b: T) -> bool { a >= b }
fn not_greater<T: PartialOrd>(a: T, b: T) -> bool { a <= b }

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

fn parse_float(f: String) -> f64 {
    f.parse().ok().unwrap()
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
fn sleep(secs: isize) {
    sleep_ms((secs * 1000) as u32);
}
fn current_time() -> f64 {
    let date_plus_cent_s = Command::new("bash")
        .arg("-c")
        .arg("python3 -c \"import time; print(time.time())\"")
        .output()
        .unwrap();
    let raw_output: Vec<u8> = date_plus_cent_s.stdout;
    let output: &str = from_utf8(&raw_output).ok().unwrap();
    let time_option: Option<f64> = output.trim().parse().ok();
    time_option.unwrap()
}
