import os
from pelican import signals  # , contents
from pelican.generators import Generator
from pelican.contents import Content

class ContentPlus(Content):
    def __init__(self, *args, **kwargs):
        super(ContentPlus, self).__init__(*args, **kwargs)
        path = os.path.split(self.source_path)
        directories = path[0]
        last_directory = os.path.split(directories)[1]
        self.slug = last_directory
        self.fname = path[1]

class PresentationMeta(ContentPlus):
    title = None
    date = None
    default_template = 'presentation'

class PresentationPage(ContentPlus):
    mandatory_properties = ('content',)
    default_template = 'presentation'
    url = None
    save_as = None
    prev_page = None
    next_page = None

    def __init__(self, *args, **kwargs):
        super(PresentationPage, self).__init__(*args, **kwargs)

        metas = kwargs["context"].get("presentation_metas", None)
        if metas:
            self.title = metas[self.slug].title
            self.date = metas[self.slug].date
        else:
            self.title = self.slug.replace('-', ' ').title()

        # add page number from filename
        page = self.fname.split('.')[0]
        if page == 'index':
            self.page = 0
        else:
            self.page = int(page)

        if self.page == 0:
            path_kwargs = {
                'slug': self.slug,
                'page': ''
            }
        else:
            path_kwargs = {
                'slug': self.slug,
                'page': self.page
            }

        url = self.settings['PRESENTATION_URL'].format(**path_kwargs)
        self.url = url.replace('//', '/')
        self.save_as = self.settings['PRESENTATION_SAVE_AS'].format(**path_kwargs)


class PresentationPageGenerator(Generator):
    def __init__(self, *args, **kwargs):
        super(PresentationPageGenerator, self).__init__(*args, **kwargs)

    def generate_context(self):
        files = self.get_files(self.settings['PRESENTATION_PATHS'])

        self.context['presentation_metas'] = self.get_presentation_metas(files)
        self.context['presentations'] = self.get_presentation_pages(files)

    def get_presentation_metas(self, files):
        presentation_metas = {}

        for f in files:
            if f.endswith("meta.md"):
                meta = self.readers.read_file(
                    base_path=self.path,
                    path=f,
                    content_class=PresentationMeta,
                    context=self.context)
                presentation_metas[meta.slug] = meta

        return presentation_metas

    def get_presentation_pages(self, files):
        presentations = []
        for f in files:
            if not f.endswith("meta.md"):
                presentation = self.readers.read_file(
                    base_path=self.path,
                    path=f,
                    content_class=PresentationPage,
                    context=self.context)
                presentations.append(presentation)

        presentations = self.add_prev_next_links(presentations)
        return presentations


    def get_presentations_by_slug(self, presentations):
        presentations_by_slug = {}
        for p in presentations:
            slug_pages = presentations_by_slug.get(p.slug)
            if slug_pages is None:
                slug_pages = presentations_by_slug[p.slug] = []

            slug_pages.append(p)

        return presentations_by_slug

    def add_prev_next_links(self, presentations):
        save_as = self.settings['PRESENTATION_URL']

        presentations_by_slug = self.get_presentations_by_slug(presentations)

        for slug, pages in presentations_by_slug.iteritems():
            for idx, p in enumerate(pages):
                prev_page = p.page - 1
                next_page = p.page + 1
                if prev_page == 0:
                    # prev_page is index of all presentations
                    p.prev_page = save_as.format(slug=p.slug, page='')
                    p.prev_page = p.prev_page.replace('//', '/')
                elif prev_page > 0:
                    p.prev_page = save_as.format(slug=p.slug, page=prev_page)

                if next_page <= len(pages) - 1:
                    p.next_page = save_as.format(slug=p.slug, page=next_page)

        return presentations

    def generate_presentation_pages(self, writer):
        for p in self.context['presentations']:
            self.context['presentation'] = p

            writer.write_file(
                self.output_path + '/' + p.save_as,
                self.get_template('presentation'),
                self.context)

        # don't pollute context with final quote
        del self.context['presentation']

    def get_presentation_first_pages(self):
        presentation_first_pages = []
        for p in self.context['presentations']:
            if p.page == 0:
                presentation_first_pages.append(p)

        presentation_first_pages = sorted(
            presentation_first_pages,
            key=lambda p: p.date, reverse=True)

        return presentation_first_pages

    def generate_presentation_index(self, writer):
        save_as = self.settings['PRESENTATION_INDEX_SAVE_AS']
        self.context['presentation_first_pages'] = self.get_presentation_first_pages()
        writer.write_file(
            save_as,
            self.get_template('presentation_index'),
            self.context)

    def generate_output(self, writer):
        self.generate_presentation_pages(writer)
        self.generate_presentation_index(writer)

def get_generators(generators):
    return PresentationPageGenerator

def register():
    signals.get_generators.connect(get_generators)
