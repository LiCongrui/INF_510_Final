import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud

#jupyter
from .const import companies, visa_years
from .mysql_db import conn, cur

# #local
# from const import companies, visa_years
# from mysql_db import conn, cur

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


def show_position_distribution():
    cur.execute("select title from positions")
    result = cur.fetchall()
    texts = []
    for item in result:
        item = item[0].split("(")[0].rstrip()
        item = re.sub(r"Sr\. |Sr |SR ", "Senior ", item)
        item = re.sub(r"Jr\. |Jr ", "Junior ", item)
        texts.append(item)
    text = '/'.join(texts)

    wc = WordCloud(max_font_size=50, background_color='white', width=800, height=600)
    wc.generate(text)

    # plot the WordCloud image
    plt.figure("Word Cloud for positions")
    plt.imshow(wc)
    plt.axis("off")
    plt.tight_layout(pad=0)

    plt.show()

def show_counts():
    stats = {}
    cur.execute("SELECT count(*) FROM positions WHERE title LIKE '%software developer%'")
    result = cur.fetchall()
    stats['software developer'] = result[0][0]

    cur.execute("SELECT count(*) FROM positions WHERE title LIKE '%data%'")
    result = cur.fetchall()
    stats['data related'] = result[0][0]

    cur.execute("SELECT count(*) FROM positions WHERE title LIKE '%analyst%'")
    result = cur.fetchall()
    stats['analyst'] = result[0][0]

    cur.execute("SELECT count(*) FROM positions WHERE title LIKE '%python%' or description LIKE '%python%'")
    result = cur.fetchall()
    stats['python'] = result[0][0]

    cur.execute("SELECT count(*) FROM positions WHERE title LIKE '%java%' or description LIKE '%java%'")
    result = cur.fetchall()
    stats['java'] = result[0][0]

    keys = list(stats.keys())
    values = list(stats.values())
    plt.barh(range(len(keys)), values, tick_label=keys)
    plt.show()

def show_tech():
    cur.execute("SELECT title FROM positions WHERE title LIKE '%software developer%'")
    result = cur.fetchall()
    print(len(result))

def search_position():
    print(1)

def show_companies():
    print(2)

if __name__ == "__main__":
    # show_visa_trending()
    # show_position_distribution()
    show_counts()