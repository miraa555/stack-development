from pathlib import Path
import re

class Stack:
    def __init__(self):
        self._data = []
    def push(self, item):
        self._data.append(item)
    def pop(self):
        if self.is_empty():
            raise ValueError("Stack underflow")
        return self._data.pop()
    def peek(self):
        if self.is_empty():
            raise ValueError("Cannot peek at empty stack")
        return self._data[-1]
    def is_empty(self):
        return len(self._data) == 0
    def __len__(self):
        return len(self._data)

PRIORITY = {'+': 1, '-': 1, '*': 2, '/': 2}
TOKEN = re.compile(r'\d+(?:\.\d+)?|[()+*/-]')

def tokenize(expression):
    tokens = TOKEN.findall(expression)
    if ''.join(tokens) != re.sub(r'\s+', '', expression):
        raise ValueError('Expression contains unsupported characters')
    return tokens

def calculate(numbers, operators):
    operator = operators.pop()
    right, left = numbers.pop(), numbers.pop()
    if operator == '+': answer = left + right
    elif operator == '-': answer = left - right
    elif operator == '*': answer = left * right
    elif operator == '/':
        if right == 0: raise ZeroDivisionError('Division by zero')
        answer = left / right
    else: raise ValueError('Invalid operator')
    numbers.push(answer)

def evaluate(expression):
    numbers, operators = Stack(), Stack()
    expecting_number = True
    tokens = tokenize(expression)
    if not tokens: raise ValueError('Empty expression')
    for token in tokens:
        if re.fullmatch(r'\d+(?:\.\d+)?', token):
            if not expecting_number: raise ValueError('Missing operator')
            numbers.push(float(token))
            expecting_number = False
        elif token == '(':
            if not expecting_number: raise ValueError('Missing operator before parenthesis')
            operators.push(token)
        elif token == ')':
            if expecting_number: raise ValueError('Missing number before closing parenthesis')
            while not operators.is_empty() and operators.peek() != '(':
                calculate(numbers, operators)
            if operators.is_empty(): raise ValueError('Unmatched closing parenthesis')
            operators.pop()
            expecting_number = False
        else:
            if expecting_number: raise ValueError('Operator without left operand')
            while (not operators.is_empty() and operators.peek() != '('
                   and PRIORITY[operators.peek()] >= PRIORITY[token]):
                calculate(numbers, operators)
            operators.push(token)
            expecting_number = True
    if expecting_number: raise ValueError('Expression ends prematurely')
    while not operators.is_empty():
        if operators.peek() == '(': raise ValueError('Unmatched opening parenthesis')
        calculate(numbers, operators)
    if len(numbers) != 1: raise ValueError('Invalid expression')
    return numbers.pop()

def format_number(value):
    return str(int(value)) if value.is_integer() else format(value, '.10g')

def process_files(input_file='input.txt', output_file='output.txt'):
    source = Path(input_file)
    if not source.exists(): raise FileNotFoundError(source)
    output = []
    for line_no, raw in enumerate(source.read_text(encoding='utf-8').splitlines(), 1):
        line = raw.strip()
        if not line or re.fullmatch(r'-{3,}', line):
            output.append(raw)
            continue
        try:
            output.append(format_number(evaluate(line)))
        except (ValueError, ZeroDivisionError) as exc:
            output.append(f'ERROR (line {line_no}): {exc}')
    Path(output_file).write_text('\n'.join(output) + '\n', encoding='utf-8')
    print(f'Processed {len(output)} lines. Results saved to {output_file}')

if __name__ == '__main__':
    process_files()
