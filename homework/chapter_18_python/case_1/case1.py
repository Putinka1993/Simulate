
import importlib
import os
import ast
import time
import multiprocessing

FORBIDDEN_NAMES = ['eval', 'exec']

def check_for_malicious_code(code, output_file):
    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in FORBIDDEN_NAMES:
                        return f"Код содержит вызов {node.func.id}()"

        return None

    except SyntaxError as e:
        return f"Код содержит синтаксическую ошибку: {type(e).__name__}"
    except Exception as e:
        return f"Код содержит вредоносные элементы: {type(e).__name__}"

def run_tests(standard_code, user_code, test_cases, output_file):
    result_etalon = []
    result_user = []

    standard_name = os.path.basename(standard_code).replace('.py', '')
    standard_module = importlib.import_module(standard_name)
    add_func_etalon = standard_module.add

    user_name = os.path.basename(user_code).replace('.py', '')
    user_module = importlib.import_module(user_name)
    add_func_user = user_module.add_numbers

    # Тестируем эталонную функцию
    for a, b in test_cases:
        result_etalon.append(add_func_etalon(a, b))

    # Флаг для предупреждения о времени
    timeout_warning_printed = False
    
    # Тестируем пользовательскую функцию с ограничением времени
    for a, b in test_cases:
        queue = multiprocessing.Queue()
        
        def process_target(q, func, x, y):
            try:
                result = func(x, y)
                q.put(('success', result))
            except Exception as e:
                q.put(('error', str(e)))
        
        process = multiprocessing.Process(
            target=process_target,
            args=(queue, add_func_user, a, b)
        )
        
        start_time = time.time()
        process.start()
        process.join(timeout=5)
        elapsed_time = time.time() - start_time
        
        if process.is_alive():
            process.terminate()
            process.join()
            result_user.append("TIMEOUT")
            
            # Выводим предупреждение только один раз
            if not timeout_warning_printed:
                print("Предупреждение: время выполнения превышает 5 секунд.")
                timeout_warning_printed = True
        else:
            if not queue.empty():
                status, value = queue.get()
                if status == 'success':
                    result_user.append(value)
                else:
                    result_user.append(f"ERROR: {value}")
            else:
                result_user.append("ERROR: результат не получен")

    # Записываем в файл
    with open(output_file, 'w') as out_f:
        # Только предупреждение, если было превышение времени
        if timeout_warning_printed:
            out_f.write("Предупреждение: время выполнения превышает 5 секунд.")
        else:
            # Если нет timeout, тогда пишем результаты тестов
            for etalon, user in zip(result_etalon, result_user):
                if etalon != user:
                    out_f.write('Тест не пройден\n')
                    out_f.write(f'Ожидаемый результат: {etalon}\n')
                    out_f.write(f'Результат пользователя: {user}\n')
                else:
                    out_f.write('Тест пройден\n')

    return


# ---------------------------

# task 1
# Чтение кодов из файлов
standard_module = 'etalon.py'
user_module = 'user.py'

test_cases = [(1, 2), (3, 4), (5, 6)]
output_file = 'output.txt'

run_tests(standard_module, user_module, test_cases, output_file)



# task 2
# ----------
# вызов функций

# Чтение кодов из файлов
standard_module = 'etalon.py'
user_module = 'user_malicious.py'

test_cases = [(1, 2), (3, 4), (5, 6)]
output_file = 'output2.txt'

with open(user_module, 'r') as f:
    user_code_content = f.read()


# Проверка на вредоносный код
malicious_code_message = check_for_malicious_code(user_code_content, output_file)
# check_for_malicious_code(user_module, output_file)
if malicious_code_message:
    with open(output_file, 'w') as f:
        f.write("Ошибка при проверке модуля user_malicious:\n")
        f.write(malicious_code_message)
else:
    run_tests(standard_module, user_module, test_cases, output_file)




# task 3
# ----------
# вызов функций 

# Чтение кодов из файлов
standard_module = 'etalon.py'
user_module = 'user_inf.py'

test_cases = [(1, 2), (3, 4), (5, 6)]
output_file = 'output3.txt'

with open(user_module, 'r') as f:
    user_code_content = f.read()

# Проверка на вредоносный код
malicious_code_message = check_for_malicious_code(user_code_content, output_file)

if malicious_code_message:
    with open(output_file, 'w') as f:
        f.write("Ошибка при проверке модуля user_malicious:\n")
        f.write(malicious_code_message)
else:
    run_tests(standard_module, user_module, test_cases, output_file)