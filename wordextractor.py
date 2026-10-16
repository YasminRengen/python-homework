import requests
import re
import click
from bs4 import BeautifulSoup

def get_html_of(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f'HTTP status code of {resp.status_code} returned, but 200 was expected. Exiting...')
        exit(1)
    return resp.content.decode()

def get_all_words_from(url):
    html = get_html_of(url)
    soup = BeautifulSoup(html, 'html.parser')
    raw_text = soup.get_text()
    return re.findall(r'\w+', raw_text)

def count_occurrences_in(word_list, min_length=0):
    word_count = {}
    for word in word_list:
        if len(word) < min_length:
            continue
        word_count[word] = word_count.get(word, 0) + 1
    return word_count

def get_top_words_from(all_words, min_length=0):
    occurrences = count_occurrences_in(all_words, min_length)
    return sorted(occurrences.items(), key=lambda item: item[1], reverse=True)

def generate_mutations(words):
    mutations = set()
    years = [str(y) for y in range(2018, 2027)]
    suffixes = ['', '1!', '2!', '3!', '01', '123', '!', '@', '#']
    for word in words:
        variants = {word, word.lower(), word.upper(), word.capitalize()}
        for v in variants:
            mutations.add(v)
            for suffix in suffixes:
                mutations.add(v + suffix)
            for y in years:
                mutations.add(v + y)
    return mutations

@click.command()
@click.option('--url', '-u', prompt='Web URL', help='URL of webpage to extract from.')
@click.option('--length', '-l', default=0, help='Minimum word length (default: 0, no limit).')
@click.option('--output', '-o', default=None, help='Output file to write results.')
def main(url, length, output):
    all_words = get_all_words_from(url)
    top_words = get_top_words_from(all_words, length)

    top_10_words = [w for w, c in top_words[:10]]
    mutations = generate_mutations(top_10_words)

    lines = [f'{word} {count}' for word, count in top_words[:10]]
    lines.append('--- mutations ---')
    lines.extend(sorted(mutations))

    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f'结果已写入 {output}')
    else:
        for line in lines:
            print(line)

if __name__ == '__main__':
    main()
