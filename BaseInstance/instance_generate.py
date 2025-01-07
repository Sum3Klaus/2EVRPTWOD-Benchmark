# -*- coding: utf-8 -*-
# @Time     : 2024-11-27-14:20
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163
import re
import os


def split_and_transform1(line):
    """对数字行进行拆分和处理"""
    # 将字符串按空格拆分成数字（仍然是字符串）
    numbers = line.split()

    # 提取从索引3开始，每两个提取一个数字
    extracted = numbers[3::2]

    result = []
    for i, num in enumerate(extracted):
        # 将数字转换为字符串
        str_num = str(num)
        if len(str_num) > 3:
            # 如果数字长度大于3，将其分割为前n-1位和最后1位
            first_part = str_num[:-1]  # 取前n-1位
            last_part = str_num[-1]  # 最后一位
            result.append(f"({int(numbers[0]) + i},{first_part},{last_part})")
        else:
            # 如果数字长度小于或等于3，分成前3位和后1位
            result.append(f"({int(numbers[0]) + i},{str_num[:3]},{str_num[3:]})")

    return " ".join(result)


def split_and_transform(line):
    # 将字符串按空格拆分成数字（仍然是字符串）
    numbers = line.split()
    data = list()
    cur_data = list()
    cnt = 0
    # start_num = int(numbers[0])
    char_pre = 0
    char_nex = 0

    for index_ in range(len(numbers)):

        if index_ % 2 == 0 and index_ > 0:
            split_chars = [char for char in numbers[index_]]
            if len(split_chars) == 4:
                char_pre = split_chars[0] + split_chars[1] + split_chars[2]
                char_nex = split_chars[-1]
            elif len(split_chars) == 5:
                char_pre = split_chars[0] + split_chars[1] + split_chars[2]
                char_nex = split_chars[-2] + split_chars[-1]

            cur_data.append(int(char_pre))
            data.append((tuple(cur_data)))
            cur_data = list()
            cur_data.append(int(char_nex))

        else:
            cur_data.append(int(numbers[index_]))

    return data


def process_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    cnt = 1
    processed_lines = []
    is_numeric_section = False  # 标记是否在需要处理的数字段落内

    for line in lines:
        line = line.strip()

        if line.startswith("Customer id, ready time, due time"):
            cnt += 1
            # 添加分隔行
            processed_lines.append("!----------------------------------------------------------------")
            # 修改标题行
            processed_lines.append(f"!{line}")
            is_numeric_section = True  # 进入需要处理的数字段落
            continue
        elif line.startswith("OD capacity:") or line.startswith("Task id"):
            # 添加分隔行
            cnt += 1
            processed_lines.append("!----------------------------------------------------------------")
            processed_lines.append(f"!{line}")
            is_numeric_section = False  # 离开需要处理的数字段落
            continue
        elif cnt == 15:
            cnt += 1
            transformed_line = split_and_transform(line)
            processed_lines.append(str(transformed_line).strip("[]"))
            # for i in transformed_line:
            #     processed_lines.append(str(i))
            continue
        elif cnt == 18:
            cnt += 1
            updated_line = re.sub(r"(\)\s*)", r"), ", line)
            processed_lines.append(updated_line)
        else:
            # 其他行直接加入
            processed_lines.append(line)
            cnt += 1


    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("\n".join(processed_lines))
        file.write("\n")


def process_data_string(data, group_size):
    """
    将字符串形式的数字按目标格式转换为括号包围的形式。
    输入: "0 37 319 461 333.0625 335.0625 47 370 437 502.388125 514.388125"
    输出: "(0,37,319,461,333.0625,335.0625,47,370,437,502.388125,514.388125)"
    """
    # 移除可能的多余空格
    # 按空格分割数据
    numbers = data.strip().split()
    # 将数据分组，每组长度为 group_size
    grouped_data = [
        f"({','.join(numbers[i:i + group_size])})"
        for i in range(0, len(numbers), group_size)
    ]
    # 将分组后的数据用逗号拼接
    return ", ".join(grouped_data)


def process_file_add_parentheses(input_file, output_file):
    """
    处理文件中的字符串行，将其转换为括号包围的格式。
    """
    cnt = 1
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    processed_lines = []
    for line in lines:
        # 判断是否为需要处理的纯数字字符串行
        if cnt == 16:
            processed_lines.append(process_data_string(line, group_size=3))
            cnt += 1
        # elif cnt == 21:
        #     processed_lines.append(process_data_string(line, group_size=11))
        else:
            processed_lines.append(line.strip())
            cnt += 1

    # 写入处理后的内容到新文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("\n".join(processed_lines) + "\n")


def add_comma_after_parentheses(input_string):
    """
    在字符串中每个')'后添加逗号','
    除最后一个括号外。
    参数:
        input_string: str, 输入的字符串
    返回:
        str, 格式化后的字符串
    """
    # 使用正则表达式在每个 ')' 后添加 ','（排除最后一个括号）
    formatted_string = re.sub(r'\)(?!\s*$)', r'),', input_string)
    return formatted_string


# Specify input and output file paths
# input_file = r"C:\Users\SumTEO\PycharmProjects\AlnsTsGba_SateSelect\NumericExperiences\03_AlnsExperiment\Operators\Experiment-2EVRP-Benchmark-Gonzalez-Perboli-Tadei-Vigo\set 3\Set3_E-n22-k4-s13-17_od_tw.txt"
# output_file = "Set3_E-n22-k4-s13-17_od_tw.txt"  # 替换为您的输出文件路径
# process_file(input_file, output_file)

folder_path = '../BenchmarkOD/Set 3/in'
output_folder = '../BenchmarkOD/Set 3/out/'

# for filename in os.listdir(folder_path):
#     # 构建文件的完整路径
#     file_path = os.path.join(folder_path, filename)
#     # print(file_path)
#
#     output_file = output_folder + filename
#     process_file(file_path, output_file)

""" 加括号 """
for filename in os.listdir(folder_path):
    # 构建文件的完整路径
    file_path = os.path.join(folder_path, filename)
    # print(file_path)

    output_file = output_folder + filename
    process_file_add_parentheses(file_path, output_file)

""" 加逗号 """
# folder_path2 = '../BenchmarkOD/Set 3/in'
# output_folder2 = '../BenchmarkOD/Set 3/out/'
#
# for filename in os.listdir(folder_path2):
#
#     file_path = os.path.join(folder_path2, filename)
#     output_file = output_folder2 + filename
#
#     cnt = 1
#     with open(file_path, 'r', encoding='utf-8') as file:
#         lines = file.readlines()
#
#     processed_lines = []
#     for line in lines:
#         # if cnt == 17 or cnt == 21:
#         if cnt == 21:
#             processed_lines.append(add_comma_after_parentheses(line))
#             cnt += 1
#         else:
#             processed_lines.append(line.strip())
#             cnt += 1
#
#     with open(output_file, 'w', encoding='utf-8') as file:
#         file.write("\n".join(processed_lines) + "\n")