# -*- coding:utf-8 -*-

from zope import schema
from StringIO import StringIO
from plone.portlets.interfaces import IPortletDataProvider
from zope.formlib import form
from plone.memoize import ram, instance
from plone.memoize.compress import xhtml_compress

from zope.interface import implements
from zope.component import getMultiAdapter

from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface import IATTopic

from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.calendar import MessageFactory as _
from plone.app.portlets import cache
from plone.app.portlets.portlets import base as base_portlet
from plone.app.portlets.portlets import calendar as base

from ZTUtils import make_query

def _render_cachekey(fun, self):
    context = aq_inner(self.context)
    if not self.updated:
        self.update()

    if self.calendar.getUseSession():
        raise ram.DontCache()
    else:
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        key = StringIO()
        print >> key, self.data.kw
        print >> key, portal_state.navigation_root_url()
        print >> key, cache.get_language(context, self.request)
        print >> key, self.calendar.getFirstWeekDay()

        year, month = self.getYearAndMonthToDisplay()
        print >> key, year
        print >> key, month
        navigation_root_path = self.root()
        start = DateTime('%s/%s/1' % (year, month))
        end = DateTime('%s/%s/1 23:59:59' % self.getNextMonth(year, month)) - 1

        def add(brain):
            key.write(brain.getPath())
            key.write('\n')
            key.write(brain.modified)
            key.write('\n\n')

        catalog = getToolByName(context, 'portal_catalog')
        path = navigation_root_path
        review_state = self.data.review_state or self.calendar.getCalendarStates()

        options = {}
        if navigation_root_path:
            root_content = self.context.restrictedTraverse(navigation_root_path)
            if IATTopic.providedBy(root_content):
                options = root_content.buildQuery()

        if options:
            # Topic
            options['start'] = {'query': end, 'range': 'max'}
            options['end'] = {'query': start, 'range': 'min'}
            if not options.get('review_state'):
                options['review_state'] = ''
            brains = catalog(**options)
        else:
            # Folder or site root
            brains = catalog(
                portal_type=self.calendar.getCalendarTypes(),
                start={'query': end, 'range': 'max'},
                end={'query': start, 'range': 'min'},
                review_state=review_state,
                path=path)

        for brain in brains:
            add(brain)

        return key.getvalue()

class ICalendarExPortlet(IPortletDataProvider):
    """A portlet displaying a calendar with selectable path
    """
    
    name = schema.TextLine(
        title=_(u"label_calendarex_title", default=u"Title"),
        description=_(u"help_calendarex_title",
                      default=u"The title of this portlet. Leave blank to "
                               "do not display portlet title."),
        default=u"",
        required=False)
    
    root = schema.Choice(
            title=_(u"label_calendarex_root_path", default=u"Root node"),
            description=_(u'help_calendarex_root',
                          default=u"You may search for and choose a folder "
                                    "to act as the root of search for this "
                                    "portlet. "
                                    "Leave blank to use the Plone site root. "
                                    "You can also select a Collection for "
                                    "get only Events found by it."),
            required=False,
            source=SearchableTextSourceBinder({'is_folderish': True},
                                              default_query='path:'))

    review_state = schema.Tuple(
         title=_(u"Review state"),
         description=_('help_review_state',
                       default=u"Filter contents using the review state. "
                                "Leave blank to use the site default. "
                                "This filter will be ignored if you select a "
                                "collection as \"Root node\""),
         default=(),
         value_type=schema.Choice(vocabulary='plone.app.vocabularies.WorkflowStates'),
         required=False)

    kw = schema.Tuple(title=_(u"Keywords"),
                     description=_('help_keywords',
                                   default=u"Keywords to be search for. "
                                            "This filter will be ignored if you select a "
                                            "collection as \"Root node\""),
                     default=(),
                     value_type=schema.TextLine()
                     )

class Assignment(base.Assignment):
    implements(ICalendarExPortlet)
    
    title = _(u'Calendar Extended')
    name = u''
    root = None
    review_state = ()
    kw = []
    
    def __init__(self, name='' ,root=None, review_state=(), kw=[]):
        self.title = name or _(u'Calendar Extended')
        self.name = name
        self.root = root
        self.review_state = review_state
        self.kw = kw
    
class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('calendar.pt')
    
    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.updated = False
    
    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())
    
    @instance.memoize
    def rootTopic(self):
        topic = self.context.restrictedTraverse(self.root())
        if IATTopic.providedBy(topic):
            return topic
        return None
    
    def topicQueryString(self):
        topic = self.rootTopic()
        return make_query(topic.buildQuery())
    
    def hasName(self):
        ''' Show title only if user informed a title in the Assignment form
        '''
        name = self.name
        name.strip()
        return name and True or False
    
    @property
    def name(self):
        return self.data.name
    
    def root(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        if self.data.root:
            navigation_root_path = '%s%s' % (portal_state.navigation_root_path(), self.data.root)
        else:
            navigation_root_path = portal_state.navigation_root_path()
        return navigation_root_path
    
    def getEventsForCalendar(self):
        context = aq_inner(self.context)
        year = self.year
        month = self.month
        navigation_root_path = self.root()
        
        options = {}
        if navigation_root_path:
            root_content = self.rootTopic()
            if root_content:
                options = root_content.buildQuery()
        
        if not options:
            # Folder, or site root
            options['path'] = navigation_root_path
            if self.data.kw:
                options['Subject'] = self.data.kw
            if self.data.review_state:
                options['review_state'] = self.data.review_state
        elif options and not options.get('review_state'):
            # if using a Topic, we need to override the calendar default behaviour with review state
            options['review_state'] = ''

        weeks = self.calendar.getEventsForCalendar(month, year, **options)
        for week in weeks:
            for day in week:
                daynumber = day['day']
                if daynumber == 0:
                    continue
                day['is_today'] = self.isToday(daynumber)
                if day['event']:
                    cur_date = DateTime(year, month, daynumber)
                    localized_date = [self._ts.ulocalized_time(cur_date, context=context, request=self.request)]
                    day['eventstring'] = '\n'.join(localized_date+[' %s' %
                        self.getEventString(e) for e in day['eventslist']])
                    day['date_string'] = '%s-%s-%s' % (year, month, daynumber)
        
        return weeks

    def getReviewStateString(self):
        states = self.data.review_state or self.calendar.getCalendarStates()
        return ''.join(map(lambda x : 'review_state=%s&amp;' % self.url_quote_plus(x), states))

class AddForm(base_portlet.AddForm):
    form_fields = form.Fields(ICalendarExPortlet)
    form_fields['root'].custom_widget = UberSelectionWidget
    label = _(u"Add Calendar Extended Portlet")
    description = _(u"This calendar portlet allows choosing a subpath.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base_portlet.EditForm):
    form_fields = form.Fields(ICalendarExPortlet)
    form_fields['root'].custom_widget = UberSelectionWidget
    label = _(u"Edit Calendar Extended Portlet")
    description = _(u"This calendar portlet allows choosing a subpath.")
