import re
import pymorphy2
import matplotlib.pyplot as plt
from collections import OrderedDict
from datetime import datetime, timedelta
import datetime

morph = pymorphy2.MorphAnalyzer()


class Tweet(object):
    tweet = ''
    time_data = datetime
    mark_average_rule = int
    mark_half_rule = int

    def __init__(self, tweet, time_data):
        tweet = re.sub(r'\n', ' ', tweet)
        tweet = re.sub(r'[«»a-zA-Z./\'":;+!?,–—()@-]', '', tweet)
        tweet = tweet.split()
        for word in tweet:
            check_pos = morph.parse(word.lower())[0].tag.POS
            normal_form = morph.parse(word.lower())[0].normal_form

            if '…' in word:
                tweet[tweet.index(word)] = ''
                continue

            if check_pos == 'PREP' or check_pos == 'PRCL' or check_pos == 'CONJ' or check_pos == 'NPRO':
                tweet[tweet.index(word)] = ''
            else:
                tweet[tweet.index(word)] = normal_form
        tweet = ' '.join(tweet)
        self.tweet = tweet
        time_data = datetime.datetime.strptime(time_data, "%Y-%m-%d %H:%M")
        self.time_data = time_data


def byname_key(Tweet):
    return Tweet.time_data


def adjust(file):
    with open(file) as f:
        tweets = f.read().split('**********')
        ar_tweets = []
        for tweet in tweets:
            tweet = re.sub(r'#\w+', '', tweet)
            date = re.findall(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}', tweet)
            text = re.findall(r'\n\D+', tweet)
            if not date:
                tweets.pop(tweets.index(tweet))
            if text:
                tw = Tweet(text[0].strip(), date[0])
                ar_tweets.append(tw)
        return ar_tweets


def hist_1(res, title):    #Построение графика
    fig = plt.figure()
    plt.hist(res)
    plt.title(title)
    plt.ylabel('Amount')
    plt.xlabel('Emotional coloring')
    plt.grid(True)
    plt.subplots_adjust(left=0.15)
    plt.show()
    # title = title + '.png'
    # plt.savefig(title, fmt='png')
    # plt.close(fig)


def hist_2(bad_adj, good_adj):
    fig = plt.figure()
    plt.xlabel('Top Five')
    ax = fig.add_subplot(211)
    ax.hist(good_adj, bins=10, facecolor='red')
    ax.grid(True)
    ax2 = fig.add_subplot(212)
    ax2.hist(bad_adj, bins=10, facecolor='blue')
    ax2.grid(True)
    plt.show()


def word_mark(word, words_data, num):       # Определение оценки
    for wd in words_data:
        temp = wd.split()
        for val in temp:
            if val == word:
                index = words_data.index(wd)
                mark = (words_data[index].split())[num]
                return mark


def frequency(data):
    count = 0
    tweets_amount = len(data)
    words_data_frequency = []
    words_data_estimations = []
    for val in data:
        temp = val.tweet.split()
        for word in temp:
            if not (word in words_data_estimations):
                for val1 in data:
                    if val1.tweet.count(word) > 0:
                        count += 1
                words_data_frequency.append(word + ' - ' + str(count) + ' - '
                                            + str(round(count / tweets_amount * 100, 1)) + '%')
                words_data_estimations.append(word)
                count = 0
    my_file = open("frequency.txt", "w")
    for line in words_data_frequency:
        my_file.write(line + '\n')
    my_file.close()
    my_file = open("estimations.txt", "w")
    for line in words_data_estimations:
        my_file.write(line + '\n')
    my_file.close()


def average_rule(tweets_analyzed):
    res = []
    amount = len(tweets_analyzed)
    total_mark = 0
    good_tw = 0
    bad_tw = 0
    neutral_tw = 0
    with open('estimations.txt') as f:
        words_data = f.read().split('\n')
    for val in tweets_analyzed:
        temp = val.tweet.split()
        if not len(temp) == 0:
            for word in temp:
                total_mark += int(word_mark(word, words_data, 2))
            total_mark /= len(temp)
            if total_mark < 50:
                bad_tw += 1
                val.mark_average_rule = -1
                res.append('Bad tweets')
            elif total_mark > 80:
                good_tw += 1
                val.mark_average_rule = 1
                res.append('Good tweets')
            else:
                neutral_tw += 1
                val.mark_average_rule = 0
                res.append('Neutral tweets')
    my_file = open("classifications.txt", "w")
    my_file.write('Average rule\n')
    my_file.write('Good' + ' - ' + str(good_tw) + ' - ' + str(round(good_tw / amount * 100, 1)) + '%' + '\n')
    my_file.write('Bad' + ' - ' + str(bad_tw) + ' - ' + str(round(bad_tw / amount * 100, 1)) + '%' + '\n')
    my_file.write('Neutral' + ' - ' + str(neutral_tw) + ' - ' + str(round(neutral_tw / amount * 100, 1)) + '%' + '\n\n')
    my_file.close()
    hist_1(res, 'Average rule')
    return tweets_analyzed


def half_rule(tweets_analyzed):
    res = []
    amount = len(tweets_analyzed)
    good_tw = bad_tw = neutral_tw = 0
    marks = []
    with open('estimations.txt') as f:
        words_data = f.read().split('\n')
    for val in tweets_analyzed:
        total_mark = 0
        temp = val.tweet.split()
        for word in temp:
            marks.append(int(word_mark(word, words_data, 1)))
        good_result = bad_result = 0
        for i in marks:
            if i == 1:
                good_result += 1
            elif i == 0:
                bad_result += 1
        if good_result > bad_result:
            n = 1
        elif bad_result > good_result:
            n = -1
        elif bad_result == good_result:
            n = 0
        for i in marks:
            if i == -n or n == 0:
                i = i/2
                total_mark += i
        if total_mark > 0:
            good_tw += 1
            val.mark_half_rule = 1
            res.append('Good tweets')
        elif total_mark < 0:
            bad_tw += 1
            val.mark_half_rule = -1
            res.append('Bad tweets')
        elif total_mark == 0:
            neutral_tw += 1
            val.mark_half_rule = 0
            res.append('Neutral tweets')
    my_file = open("classifications.txt", "a")
    my_file.write('Half rule\n')
    my_file.write('Good' + ' - ' + str(good_tw) + ' - ' + str(round(good_tw / amount * 100, 1)) + '%' + '\n')
    my_file.write('Bad' + ' - ' + str(bad_tw) + ' - ' + str(round(bad_tw / amount * 100, 1)) + '%' + '\n')
    my_file.write('Neutral' + ' - ' + str(neutral_tw) + ' - ' + str(round(neutral_tw / amount * 100, 1)) + '%' + '\n\n')
    my_file.close()
    hist_1(res, "Half rule")
    return tweets_analyzed


def top_adj(tweets_analyzed):
    bad_adj_list = []
    good_adj_list = []
    amount = len(tweets_analyzed)
    bad_adj = {}
    good_adj = {}
    with open('estimations.txt') as f:
        words_mark = f.read().split('\n')
    with open('frequency.txt') as g:
        words_frequency = g.read().split('\n')
    for word in words_mark:
        temp_1 = word.split()
        check_pos = morph.parse(temp_1[0])[0].tag.POS
        if check_pos == 'ADJF' or check_pos == 'ADJS':
            for freq in words_frequency:
                temp_2 = freq.split(' - ')
                if temp_2[0] == temp_1[0] and temp_1[1] == '-1':
                    bad_adj[temp_1[0]] = int(temp_2[1])
                    break
                if temp_2[0] == temp_1[0] and temp_1[1] == '1':
                    good_adj[temp_1[0]] = int(temp_2[1])
                    break
    good_adj = OrderedDict(sorted(good_adj.items(), key=lambda x: x[1], reverse=True))
    my_file = open("adjectives.txt", "w")
    counter = 0
    my_file.write('Top-5 Positive:' + '\n')
    for key in good_adj:
        if counter > 4:
            break
        for i in range(0, int(good_adj[key])):
            good_adj_list.append(key)
        counter += 1
        my_file.write(key + ' - ' + str(good_adj[key]) + ' - ' + str(round(int(good_adj[key]) / amount, 5)) + '%\n')
    my_file.write('\n')
    bad_adj = OrderedDict(sorted(bad_adj.items(), key=lambda x: x[1], reverse=True))
    counter = 0
    my_file.write('Top-5 Negative:' + '\n')
    for key in bad_adj:
        if counter > 4:
            break
        for i in range(0, int(bad_adj[key])):
            bad_adj_list.append(key)
        counter += 1
        my_file.write(key + ' - ' + str(bad_adj[key]) + ' - ' + str(round(int(bad_adj[key])/amount, 5)) + '%\n')
    hist_2(bad_adj_list, good_adj_list)
    my_file.write('\n')
    my_file.close()


def distribution(ar_tweets):
    time_manage = []
    bad_manage = []
    good_manage = []
    nei_manage = []
    ar_tweets = sorted(ar_tweets, key=byname_key)
    min = 30
    my_file = open("hours.txt", "w")
    tweet_res = []
    start = ar_tweets[0].time_data
    end = ar_tweets[len(ar_tweets) - 1].time_data
    trig = True
    while trig:
        time_manage.append(str((start + timedelta(minutes=min)).time()))
        pos = 0
        neg = 0
        nei = 0
        tweet_res.clear()
        for val in ar_tweets:
            if start <= val.time_data and val.time_data <= start + timedelta(minutes=min):
                tweet_res.append(val)
        for tw in tweet_res:
            if tw.mark_average_rule == 1:
                pos += 1
            elif tw.mark_average_rule == -1:
                neg += 1
            elif tw.mark_average_rule == 0:
                nei += 1
        bad_manage.append(neg / len(tweet_res))
        good_manage.append(pos / len(tweet_res))
        nei_manage.append(nei / len(tweet_res))
        my_file.write(str(start.time()) + '-' + str((start + timedelta(minutes=min)).time()) + ' '
                        + str(len(tweet_res)) + ' ' + str(round(pos / len(tweet_res), 2)) +
                        '/' + str(round(neg / len(tweet_res), 2)) + '/' +
                        str(round(nei / len(tweet_res), 2)) + '\n')
        min += 10
        if start + timedelta(minutes=min) > end:
            break
    grap(time_manage,bad_manage, good_manage,nei_manage)


def grap(time_manage,bad_manage, good_manage,nei_manage):
    colors = ['red', 'blue', 'green']
    f_plot(time_manage, bad_manage, time_manage, good_manage,time_manage, nei_manage, colors=colors, linewidth=2.)


def f_plot(*args, **kwargs):
    xlist = []
    ylist = []
    for i, arg in enumerate(args):
        if i % 2 == 0:
            xlist.append(arg)
        else:
            ylist.append(arg)
    colors = kwargs.pop('colors', 'k')
    linewidth = kwargs.pop('linewidth', 1.)
    fig = plt.figure()
    ax = fig.add_subplot(211)
    i = 0
    for x, y, color in zip(xlist, ylist, colors):
        i += 1
        ax.plot(x, y, color=color, linewidth=linewidth)
    ax.grid(True)
    plt.subplots_adjust(left=0.15)
    fig.savefig('distribution')
    fig.show()


trigger = False
ar_tweets = adjust('tweets.txt')
# if trigger:
#     frequency(ar_tweets)
ar_tweets = average_rule(ar_tweets)
# ar_tweets = half_rule(ar_tweets)
top_adj(ar_tweets)
# distribution(ar_tweets)