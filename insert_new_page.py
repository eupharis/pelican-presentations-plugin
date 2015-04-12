#!/usr/bin/python
import os
from optparse import OptionParser


def sort_page(page):
    p = page.split('.')[0]
    try:
        p = int(p)
        return p
    except ValueError:
        return 0


def touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'a').close()


def insert_page(insert_idx):
    '''
    create a new page at insert_idx
    renumber all subsequent slides (+1)
    '''
    pages = os.listdir('.')
    pages = sorted(pages, key=sort_page)
    while len(pages):
        p = pages.pop()
        num, ext = p.split('.')
        try:
            num = int(num)
            if (num < insert_idx):
                new_page = '{}.{}'.format(insert_idx, ext)
                print 'creating: {}'.format(new_page)
                touch(new_page)
                break
            else:
                new_page = '{}.{}'.format(num + 1, ext)
                print 'making page {} into {}'.format(p, new_page)
                os.rename(p, new_page)

        except ValueError, e:
            if num == 'index' and insert_idx == 1:
                # handle first page!
                new_page = '1.{}'.format(ext)
                print 'creating: {}'.format(new_page)
                touch(new_page)
            else:
                print e
            break


def main():
    parser = OptionParser("./%prog [page_number]\n\tScript to insert new page at page_number and increment all subsequent pages")

    (options, args) = parser.parse_args()

    print options
    print args
    if len(args) == 0:
        parser.error("Page number to insert new page at not given.")
        return
    if len(args) > 1:
        parser.error("Multiple page number arguments provided. Please provide only one page number argument.")
        return

    page_number = None
    try:
        page_number = int(args[0])
    except ValueError:
        parser.error("Error: page number is not a number")
        return

    insert_page(page_number)


if __name__ == '__main__':
    main()
