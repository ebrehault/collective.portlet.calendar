# -*- coding:utf-8 -*-

from Acquisition import aq_inner
from DateTime import DateTime
from Products.ATContentTypes.interfaces import IATTopic
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish
from Products.ATContentTypes.interfaces.folder import IATFolder
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from StringIO import StringIO
from ZTUtils import make_query
from collective.portlet.calendar import MessageFactory as _
from plone.app.collection.interfaces import ICollection
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.querystring.queryparser import parseFormquery
from plone.app.portlets import cache
from plone.app.portlets.portlets import base as base_portlet
from plone.app.portlets.portlets import calendar as base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.memoize import ram, instance
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements


def add_cachekey(key, brain):
    key.write(brain.getPath())
    key.write('\n')
    key.write(brain.modified)
    key.write('\n\n')


def _define_search_options(renderer, options):
    """Obtain a proper query to be used in search"""
    catalog = getToolByName(renderer.context, 'portal_catalog')
    all_review_states = list(catalog.uniqueValuesFor('review_state'))
    if not options:
        # Folder, or site root.
        options['path'] = renderer.root()
        if renderer.data.kw:
            options['Subject'] = renderer.data.kw
        options['review_state'] = renderer.data.review_state \
            if renderer.data.review_state else all_review_states
    else:
        # Collection
        # Type check: seems that new style collections are returning parameters as tuples
        # this is not compatible with ZTUtils.make_query
        untuple(options)
        # We must handle in a special way "start" and "end" criteria
        if 'start' in options.keys():
            renderer._fix_range_criteria('start')
        if 'end' in options.keys():
            renderer._fix_range_criteria('end')
        if not options.get('review_state'):
            # We need to override the calendar default behaviour with review state
            options['review_state'] = all_review_states
    return options


def _render_cachekey(fun, self):
    context = aq_inner(self.context)
    if not self.updated:
        self.update()

    if self.calendar.getUseSession():
        raise ram.DontCache()
    else:
        portal_state = getMultiAdapter(
            (context, self.request), name=u'plone_portal_state')
        key = StringIO()
        print >> key, self.data.kw
        print >> key, self.data.review_state
        print >> key, self.data.name
        print >> key, portal_state.navigation_root_url()
        print >> key, cache.get_language(context, self.request)
        print >> key, self.calendar.getFirstWeekDay()

        year, month = self.getYearAndMonthToDisplay()
        print >> key, year
        print >> key, month
        navigation_root_path = self.root()
        start = DateTime('%s/%s/1' % (year, month))
        end = DateTime('%s/%s/1 23:59:59' % self.getNextMonth(year, month)) - 1

        catalog = getToolByName(context, 'portal_catalog')

        self.options = {}
        if navigation_root_path:
            root_content = self.context.restrictedTraverse(navigation_root_path)
            if IATTopic.providedBy(root_content):
                self.options = root_content.buildQuery()
            elif ICollection.providedBy(root_content):
                self.options = parseFormquery(root_content,
                                              root_content.getField('query').getRaw(root_content))
            print >> key, root_content.modified()

        self.options['start'] = {'query': end, 'range': 'max'}
        self.options['end'] = {'query': start, 'range': 'min'}

        _define_search_options(self, self.options)
        brains = catalog(**self.options)

        for brain in brains:
            add_cachekey(key, brain)

        return key.getvalue()


class ICalendarExPortlet(IPortletDataProvider):
    """A portlet displaying a calendar with selectable path
    """

    name = schema.TextLine(
        title=_(u'label_calendarex_title', default=u'Title'),
        description=_(
            u'help_calendarex_title',
            default=u'The title of this portlet. Leave blank to '
                    u'do not display portlet title.'),
        default=u"",
        required=False)

    root = schema.Choice(
        title=_(u'label_calendarex_root_path', default=u'Root node'),
        description=_(
            u'help_calendarex_root',
            default=u'You may search for and choose a folder '
                    u'to act as the root of search for this '
                    u'portlet. '
                    u'Leave blank to use the Plone site root. '
                    u'You can also select a Collection for '
                    u'get only Events found by it.'),
        required=False,
        source=SearchableTextSourceBinder(
            {'object_provides': [IATTopic.__identifier__,
                                 ICollection.__identifier__,
                                 IFolderish.__identifier__,
                                 IATFolder.__identifier__]},
            default_query='path:'))

    review_state = schema.Tuple(
        title=_(u'Review state'),
        description=_(
            'help_review_state',
            default=u'Filter contents using the review state. '
                    u'Leave blank to use the site default. '
                    u'This filter will be ignored if you select a '
                    u'collection as "Root node"'),
        default=(),
        value_type=schema.Choice(
            vocabulary='plone.app.vocabularies.WorkflowStates'),
        required=False)

    kw = schema.Tuple(
        title=_(u'Keywords'),
        description=_(
            'help_keywords',
            default=u'Keywords to be search for. '
                    u'This filter will be ignored if '
                    u'you select a collection as '
                    u'"Root node"'),
        default=(),
        value_type=schema.TextLine()
    )


def untuple(options):
    """Seems that catalog only talk well with list, not tuples"""
    for k, v in options.items():
        if isinstance(v, tuple):
            options[k] = list(v)
        elif isinstance(v, dict):
            untuple(v)


class Assignment(base.Assignment):
    implements(ICalendarExPortlet)

    name = u''
    root = None
    review_state = ()
    kw = []

    def __init__(self, name='', root=None, review_state=(), kw=[]):
        self.name = name
        self.root = root
        self.review_state = review_state
        self.kw = kw

    @property
    def title(self):
        return _('portlet_title',
                 u'Calendar Extended: $name',
                 mapping={'name': self.name or 'unnamed'})


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('calendar.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.updated = False
        self.options = {}

    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @instance.memoize
    def rootTopic(self):
        topic = self.context.restrictedTraverse(self.root())
        if IATTopic.providedBy(topic) or ICollection.providedBy(topic):
            return topic
        return None

    def topicQueryString(self):
        # BBB: seems ununsed
        topic = self.rootTopic()
        if IATTopic.providedBy(topic):
            return make_query(topic.buildQuery())
        else:
            raise NotImplementedError('No support for %s yet' % topic.portal_type)

    def hasName(self):
        ''' Show title only if user informed a title in the Assignment form
        '''
        return bool(self.name.strip())

    @property
    def name(self):
        return self.data.name or ''

    def root(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state')
        if self.data.root:
            navigation_root_path = '%s%s' % (portal_state.navigation_root_path(), self.data.root)
        else:
            navigation_root_path = portal_state.navigation_root_path()
        return navigation_root_path

    def collection_querystring(self):
        return make_query(self.options)

    def _fix_range_criteria(self, index):
        """
        Calendar commonly preset criteria like these:
            'start': {'query': last_date, 'range': 'max'}
            'end': {'query': first_date, 'range': 'min'}
        We must take care of collections that already use start or end criteria and be
        sure that we don't allow dates outside the current month
        """
        year = self.year
        month = self.month
        criteria = self.options[index]
        if not isinstance(criteria['query'], list):
            criteria['query'] = [criteria['query']]
        # New style collection return a string for date criteria... awful but true
        criteria['query'] = [DateTime(d) if isinstance(d, basestring) else d for d in criteria['query']]
        # keep only dates inside the current month
        criteria['query'] = [d for d in criteria['query'] if d.year() == year and d.month() == month]

        if index == 'start':
            last_day = self.calendar._getCalendar().monthrange(year, month)[1]
            calendar_date = self.calendar.getBeginAndEndTimes(last_day, month, year)[1]
            # add the last day in the month only if smaller than collection's date
            if not criteria['query'] or calendar_date < max(criteria['query']) or criteria['range'] != 'max':
                criteria['query'].append(calendar_date)
            if criteria['range'] == 'min':
                criteria['range'] = 'minmax'
        elif index == 'end':
            calendar_date = self.calendar.getBeginAndEndTimes(1, month, year)[0]
            # add the fist day in the month only if greater than collection's date
            if not criteria['query'] or calendar_date > min(criteria['query']) or criteria['range'] != 'min':
                criteria['query'].append(calendar_date)
            if criteria['range'] == 'max':
                criteria['range'] = 'minmax'
        self.options[index] = criteria

    def getEventsForCalendar(self):
        navigation_root_path = self.root()

        self.options = {}
        if navigation_root_path:
            root_content = self.rootTopic()
            if root_content:
                if IATTopic.providedBy(root_content):
                    self.options = root_content.buildQuery()
                elif ICollection.providedBy(root_content):
                    self.options = parseFormquery(root_content, root_content.getField('query').getRaw(root_content))

        _define_search_options(self, self.options)
        weeks = self._get_calendar_structure()
        return weeks

    def _get_calendar_structure(self):
        context = aq_inner(self.context)
        year = self.year
        month = self.month
        weeks = self.calendar.getEventsForCalendar(month, year, **self.options)
        for week in weeks:
            for day in week:
                daynumber = day['day']
                if daynumber == 0:
                    continue
                day['is_today'] = self.isToday(daynumber)
                if day['event']:
                    cur_date = DateTime(year, month, daynumber)
                    localized_date = [self._ts.ulocalized_time(cur_date, context=context, request=self.request)]
                    day['eventstring'] = '\n'.join(
                        localized_date + [' %s' % self.getEventString(e) for e in day['eventslist']])
                    day['date_string'] = '%s-%s-%s' % (year, month, daynumber)
        return weeks

    def getReviewStateString(self):
        states = self.data.review_state or self.calendar.getCalendarStates()
        return ''.join(map(lambda x: 'review_state=%s&' % self.url_quote_plus(x), states))


class AddForm(base_portlet.AddForm):
    form_fields = form.Fields(ICalendarExPortlet)
    form_fields['root'].custom_widget = UberSelectionWidget
    label = _(u'Add Calendar Extended Portlet')
    description = _(u'This calendar portlet allows choosing a subpath.')

    def create(self, data):
        return Assignment(**data)


class EditForm(base_portlet.EditForm):
    form_fields = form.Fields(ICalendarExPortlet)
    form_fields['root'].custom_widget = UberSelectionWidget
    label = _(u'Edit Calendar Extended Portlet')
    description = _(u'This calendar portlet allows choosing a subpath.')
