import re, math, pickle
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
# from mpl_toolkits.basemap import Basemap #if jupyter, comment it out
# from geopy.geocoders import Nominatim  #if jupyter, comment it out

#jupyter use this 2
from .const import companies, visa_years, us_states, salaries
from .mysql_db import conn, cur

# #local use this 2
# from const import companies, visa_years, us_states, salaries
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


def search_position(title = '', loc = '', comp = ''):
    cur.execute("SELECT * FROM positions where title LIKE '%{}%' and location like '%{}%' limit 20".format(title, loc))
    result = cur.fetchall()
    df = pd.DataFrame(list(result))
    if df.shape[0] > 0 and comp != '':
        df2 = df[df['company'].str.contains(comp)]
        return df2
    else:
        return df

def show_companies():
    cur.execute("SELECT location, count(*) num FROM companies group by location ORDER by num desc LIMIT 50;")
    result = cur.fetchall()
    cities = []
    for item in result:
        parts = item[0].split(",")
        if len(parts) > 1:
            cities.append([parts[0], item[1]])
        else:
            cities.append([us_states[parts[0]], item[1]])
    scale = 5

    bmp = Basemap(llcrnrlon=-119, llcrnrlat=22, urcrnrlon=-64, urcrnrlat=49,
                projection='lcc', lat_1=33, lat_2=45, lon_0=-95, width=1000, height=800)

    bmp.drawstates()
    bmp.drawcountries()
    bmp.drawcoastlines()
    bmp.fillcontinents(lake_color='lightskyblue')

    # Get the location of each city and plot it
    # lazy loading loc with pickle
    try:
        geo_dict = pickle.load(open("geo_loc", "rb"))
    except:
        geo_dict = {}
    key_count = len(geo_dict.keys())

    geolocator = Nominatim(user_agent = 'INF510Proj')
    for (city, count) in cities:
        if city in geo_dict.keys():
            (x, y) = geo_dict[city]
        else:
            loc = geolocator.geocode(city)
            x, y = bmp(loc.longitude, loc.latitude)
            geo_dict[city] = (x, y)
        bmp.plot(x, y, marker='o', color='Red', markersize=int(math.sqrt(count)) * scale)
        plt.text(x, y, city, fontdict={'size': 5})
    plt.show()

    if key_count < len(geo_dict.keys()):
        pickle.dump(geo_dict, open( "geo_loc", "wb" ) )

def compare_salary():
    cur.execute("SELECT title, avg(base_pay) FROM salaries group by title;")
    result = cur.fetchall()
    X = []
    Y = []
    for item in result:
        X.append(item[0])
        Y.append(item[1])

    plt.bar(X, Y, 0.4)
    plt.xlabel("Job type")
    plt.ylabel("Avg salary")
    plt.title("Average salary of 4 main positions")

    plt.show()

    return result

def top_companies(sort_by='positions'):
    for title in salaries.keys():
        data = {
            'company': [],
            'base_pay': [],
            'positions': []
        }
        cur.execute("SELECT company, base_pay, positions FROM salaries "+
                    "where title = '{}' order by {} desc limit 10".format(title, sort_by))
        result = cur.fetchall()
        for item in result:
            data['company'].append(item[0])
            data['base_pay'].append(item[1])
            data['positions'].append(item[2])

        df = pd.DataFrame(data)
        print(title)
        print(df)
        print()

if __name__ == "__main__":
    # show_visa_trending()
    # show_position_distribution()
    # show_counts()
    # show_companies()
    # compare_salary()
    top_companies()
