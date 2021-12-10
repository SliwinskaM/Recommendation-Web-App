import numpy as np
import matplotlib.pyplot as plt
import csv

########## Wizualizacja macierzy ################################
def write_r_matrix(data, conv_r_matrix, curves):
    with open('matrixR.csv', 'w', newline='') as csvfile:
        r_writer = csv.writer(csvfile, delimiter=',')
        tmp_first = [""]
        for i in range(len(data.products)):
            tmp_first += [str(data.products[i])]
        r_writer.writerow(tmp_first)
        for row in range(len(conv_r_matrix)):
            tmp_row = []
            tmp_row += [str(data.users[row])]
            for rating in conv_r_matrix[row]:
                tmp = [""]
                if np.all(~np.isnan(rating)):
                    for curve in range(len(curves.Names)):
                        tmp[0] += curves.Names(curve).name + ":" + str(round(rating[curve], 2)) + "\n"
                tmp_row += tmp
            try:
                r_writer.writerow(tmp_row)
            except UnicodeEncodeError as e:
                r_writer.writerow(['-'])



def write_rules(data, rules, confidences, supports, curves):
    with open('Rules.csv', 'w', newline='') as csvfile:
        r_writer = csv.writer(csvfile, delimiter=',')
        for i in range(len(rules)):
            antec, conseq = rules[i]
            conf = confidences[i]
            sup = supports[i]
            tmp_row = []
            tmp_row += [str(conf[0])]
            tmp_row += [np.round(sup, 4)]
            tmp = [""]
            for a in antec:
                prod = data.products[a[0]]
                score = curves.Names(a[1]).name
                tmp[0] += "[" + prod + ": " + score + "]; "
            tmp_row += tmp
            tmp_row += ["->"]
            tmp2 = [""]
            for c in conseq:
                prod = data.products[c[0]]
                score = curves.Names(c[1]).name
                tmp2[0] += "[" + prod + ": " + score + "]; "
            tmp_row += tmp2
            try:
                r_writer.writerow(tmp_row)
            except UnicodeEncodeError as e:
                r_writer.writerow(['-'])


def write_recomms(data, user_recomms):
    with open('Recommendations.csv', 'w', newline='') as csvfile:
        r_writer = csv.writer(csvfile, delimiter=',')
        for user in user_recomms:
            tmp_row = []
            tmp_row += [data.users[user]]
            tmp_row += ["->"]
            tmp2 = [""]
            for r in user_recomms[user]:
                prod = data.products[r]
                tmp2[0] += prod + "; "
            tmp_row += tmp2
            try:
                r_writer.writerow(tmp_row)
            except UnicodeEncodeError as e:
                r_writer.writerow(['-'])


# Wizualizacja funkcji przynależności
# ########### PLOTS #######################
def plot_fuzzy(data, fc, sets_num, p1, p2, p3, p4):
    x = np.linspace(0.0, 1.0, num=1000)
    sc = np.linspace(1.0, 5.0, num=1000)
    # 3 sets
    if sets_num == 3:
        y1 = [fc.Curves1(data.min_score, data.max_score, p1, p2, p3, p4).low_curve(i) for i in sc]
        y2 = [fc.Curves1(data.min_score, data.max_score, p1, p2, p3, p4).medium_curve(i) for i in sc]
        y3 = [fc.Curves1(data.min_score, data.max_score, p1, p2, p3, p4).high_curve(i) for i in sc]
        plt.plot(x, y1, 'mediumblue')
        plt.plot(x, y2, 'g')
        plt.plot(x, y3, 'r')
        for p in p1, p2, p3, p4:
            plt.axvline(p, c='grey', ls="--")
            plt.text(p, 1.07, str(p), horizontalalignment='center')
        plt.legend(['Low', 'Medium', 'High'], loc="center right", bbox_to_anchor=(1.1, 0.5))

    # 2 sets
    if sets_num == 2:
        y4 = [fc.Curves2(data.min_score, data.max_score, p1, p2).low_curve(i) for i in sc]
        y5 = [fc.Curves2(data.min_score, data.max_score, p1, p2).high_curve(i) for i in sc]
        plt.plot(x, y4, 'mediumblue')
        plt.plot(x, y5, 'r')
        for p in p1, p2:
            plt.axvline(p, c='grey', ls="--")
            plt.text(p, 1.07, str(p), horizontalalignment='center')
        plt.legend(['Low', 'High'], loc="center right", bbox_to_anchor=(1.1, 0.5))

    # common part
    plt.text(0.5, 1.15, 'Punkty graniczne', horizontalalignment='center')
    plt.xlabel('Rozmyta ocena')
    plt.ylabel('Przynależność do zbioru')
    plt.savefig('fuzzy_curve_2_pred.png', format="png")
    plt.show()
