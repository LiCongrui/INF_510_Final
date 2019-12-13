from const import companies, visa_years
from mysql_db import create_tables, conn, cur
import matplotlib.pyplot as plt

def show_visa_trending():
    for comp in companies:
        y = []
        for year in visa_years:
            cur.execute("select * from visa_records where sponsor = '{}' and ryear = '{}'".format(comp, str(year)))
            result = cur.fetchall()
            if len(result) > 0:
                if len(result) > 1:
                    nums = [x[3] for x in result]
                    y.append(sum(nums))
                else:
                    y.append(result[0][3])
        plt.plot(visa_years, y, label=comp)

    plt.title('The trending of visa sponsors')
    plt.xlabel('year')
    plt.ylabel('LCA number')
    plt.legend(loc = "best")
    plt.show()

def search_position(title):
    pass

def show_companies():
    pass

if __name__ == "__main__":
    show_visa_trending()