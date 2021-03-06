import concurrent.futures
import time
import csv


# Arrondi à deux décimales
def round_float(arg):
    return round(float(arg), 2)


# 1 - Lecture du csv avec calcul du bénéfice
def csv_read_threaded(file_arg):
    """Read the selected cv file and return a list including a calculated benefit"""
    print(f"Reading {file_arg}...")
    with open(file_arg, newline='') as csv_file:
        spamreader = csv.reader(csv_file, delimiter=',', quotechar='|')
        next(spamreader)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list_csv = list(executor.map(lambda x: benefit_row_calculator(x), spamreader))
    return list_csv


# Calcul du bénéfice
def benefit_row_calculator(row):
    row_calculated = [row[0], float(row[1]), float(row[2])] + [round(float((float(row[1]) * float(row[2]) / 100)), 2)]
    return row_calculated


# 2 - Nettoyage des actions à prix nul ou négatif
def value_cleaner(list_arg, x):
    """Clean shares having a null or negative price"""
    if x[1] > 0:
        return list_arg.append(x)
    else:
        return 0


def threaded_clean_list(list_arg):
    """Threading the cleaning function to improve efficiency"""
    list_clean = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        list(executor.map(lambda x: (value_cleaner(list_clean, x)), list_arg))
    return list_clean


# 3 - Algorithme du sac à dos
def knap_sack_list_name(budget_total_w, list_arg, n):
    """Knapsack algorithm, including share names

    Args : total cash, complete shares list, len(list)
    Return : cash spent, benefit, selected shares list"""
    total_price = 0.0
    k = [[[0, ""] for x in range(budget_total_w + 1)] for x in range(n + 1)]
    for i in range(n + 1):
        for j in range(budget_total_w + 1):
            if i == 0 or j == 0:
                k[i][j][0] = 0
                k[i][j][1] = ""
            elif list_arg[i - 1][1] <= j:
                knap_one = list_arg[i - 1][-1] + k[i - 1][int(j - list_arg[i - 1][1])][0]
                knap_two = k[i - 1][j][0]
                if knap_one > knap_two:
                    k[i][j][0] = knap_one
                    k[i][j][1] = list_arg[i - 1][0] + ", " + k[i - 1][int(j - list_arg[i - 1][1])][1]
                    total_price = budget_total_w - list_arg[i - 1][1]
                else:
                    k[i][j][0] = knap_two
                    k[i][j][1] = k[i - 1][j][1]
            else:
                k[i][j][0] = k[i - 1][j][0]
                k[i][j][1] = k[i - 1][j][1]
    return total_price, round_float(k[n][budget_total_w][0]), k[n][budget_total_w][1]


# Précision
def precision_input():
    """User selection of the algorithm precision"""
    precision_select = "1,10,100"
    precision = input("Select precision :\n"
                      "1 - à l'euro\n"
                      "10 - au dixième d'euro\n"
                      "100 - au centime\n")
    if precision in precision_select:
        return precision
    else:
        precision_input()


def precision_fold(list_arg, fold_arg=1):
    list_arg[1] = list_arg[1] * fold_arg
    return list_arg


def precision_print(fold_arg):
    if fold_arg == 1:
        return "à l'euro"
    if fold_arg == 10:
        return "au dixième d'euro"
    if fold_arg == 100:
        return "au centime d'euro"
    else:
        return "precision fold incorrect"


def file_print():
    file_selected = input(f"""Select a file :
      1 - .\dataset1_Python+P7.csv
      2 - .\dataset2_Python+P7.csv
      3 - Enter a new file path""")
    if file_selected == "1":
        return ".\dataset1_Python+P7.csv"
    elif file_selected == "2":
        return ".\dataset2_Python+P7.csv"
    elif file_selected == "3":
        return input("Enter file path : ")
    else:
        print("Select anew")
        file_print()


# Fonction de print
def print_result(tuple_arg, timing, n, fold_arg):
    """Algorithm report view"""
    precision = precision_print(fold_arg)
    share_list = tuple_arg[2].split(", ")
    share_list.pop()
    share_list.reverse()
    timing = round(timing, 4)
    check = round(timing / n, 4)
    print(f"""Algorithme terminé :
    Actions pertinentes étudiées : {n}
    Précision : {precision}
    Temps écoulé : {timing} secondes ({check}s/n)
    Bénéfice : {tuple_arg[1]}
    Actions sélectionnées : {share_list}""")


# Fonction d'algorithme complet
def complete_algorithm(budget_total_w, list_arg, start_time, fold_arg=1):
    """Complete algorithm, from raw share_list to result_printing

    Execution :
    1- cleaning the list
    2- applying precision
    3- knapsack algorithm
    4- printing report"""
    list_clean = threaded_clean_list(list_arg)
    n = len(list_clean)
    budget_total_w = budget_total_w * fold_arg
    list_ten = list(map(lambda x: precision_fold(x, fold_arg), list_clean))
    result_fast = knap_sack_list_name(budget_total_w, list_ten, n)
    end = time.time()
    timing = end - start_time
    print_result(result_fast, timing, n, fold_arg)
    return result_fast, timing


w = int(input("Enter total cash amount : "))
fold = int(precision_input())
file = file_print()
# W = 500
# fold = 1
# file = "C:\opc finis\Projet 7\data\dataset1_Python+P7.csv"

start_one = time.time()
list_csv_threaded = csv_read_threaded(file)
complete_algorithm(w, list_csv_threaded, start_one, fold)

# print("")
#
# file_two = "C:\opc finis\Projet 7\data\dataset2_Python+P7.csv"
#
# start_two = time.time()
# list_csv_threaded_two = csv_read_threaded(file_two)
# complete_algorithm(w, list_csv_threaded_two, start_two, fold)
