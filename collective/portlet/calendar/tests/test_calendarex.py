import unittest2 as unittest
from DateTime import DateTime
from Products.GenericSetup.utils import _getDottedName
from collective.portlet.calendar import calendar
from collective.portlet.calendar.calendar import Renderer
from collective.portlet.calendar.testing import INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from zope.component import getUtility, getMultiAdapter


class TestPortlet(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.CalendarEx')
        self.assertEquals(portlet.addview, 'portlets.CalendarEx')

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name='portlets.CalendarEx')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEquals(['plone.app.portlets.interfaces.IColumn',
          'plone.app.portlets.interfaces.IDashboard'],
          registered_interfaces)

    def testInterfaces(self):
        portlet = calendar.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.CalendarEx')
        mapping = self.portal.restrictedTraverse(
                                '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'name': 'My Calendar',
                                   'root': u''})
        self.assertEquals(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], calendar.Assignment))

    def testPortletProperties(self):
        portlet = getUtility(IPortletType, name='portlets.CalendarEx')
        mapping = self.portal.restrictedTraverse(
                                '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={'name': 'My Calendar',
                                   'root': u''})
        name = mapping.values()[0].name
        root = mapping.values()[0].root
        self.assertEqual(name, 'My Calendar')
        self.assertEqual(root, u'')

    def testRenderer(self):
        context = self.portal
        request = self.portal.REQUEST
        view = self.portal.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)
        assignment = calendar.Assignment()

        renderer = getMultiAdapter((context, request, view,
                                    manager, assignment), IPortletRenderer)
        self.assertTrue(isinstance(renderer, calendar.Renderer))


class TestRendererBase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.renderer = Renderer(self.layer['portal'], self.layer['request'],
                                 None, None, {})
        year = 2014
        month = 5
        self.renderer.update()
        calendar = self.renderer.calendar
        last_day = calendar._getCalendar().monthrange(year, month)[1]
        self.first_date = calendar.getBeginAndEndTimes(1, month, year)[0]
        self.last_date = calendar.getBeginAndEndTimes(last_day, month, year)[1]
        self.renderer.year = year
        self.renderer.month = month

    def test_fix_range_criteria_start(self):
        renderer = self.renderer
        d1 = DateTime('2014/05/10')
        renderer.options = {'start': {'query': d1, 'range': 'min'}}
        renderer._fix_range_criteria('start')
        self.assertEqual(renderer.options,
                         {'start': {'query': [d1, self.last_date],
                                    'range': 'minmax'}})
        d1 = DateTime('2014/05/25')
        renderer.options = {'start': {'query': d1, 'range': 'max'}}
        renderer._fix_range_criteria('start')
        self.assertEqual(renderer.options,
                         {'start': {'query': [d1, self.last_date],
                                    'range': 'max'}})
        d1 = DateTime('2014/05/10')
        d2 = DateTime('2014/06/08')
        renderer.options = {'start': {'query': [d1, d2], 'range': 'minmax'}}
        renderer._fix_range_criteria('start')
        self.assertEqual(renderer.options,
                         {'start': {'query': [d1, self.last_date],
                                    'range': 'minmax'}})

    def test_fix_range_criteria_start_new_collection(self):
        # WTF: new style collections are returning "strings"
        renderer = self.renderer
        d1 = '2014/05/10'
        renderer.options = {'start': {'query': d1, 'range': 'min'}}
        renderer._fix_range_criteria('start')
        self.assertEqual(renderer.options,
                         {'start': {'query': [DateTime(d1), self.last_date],
                                    'range': 'minmax'}})
        d1 = DateTime('2014/05/25')
        renderer.options = {'start': {'query': d1, 'range': 'max'}}
        renderer._fix_range_criteria('start')
        self.assertEqual(renderer.options,
                         {'start': {'query': [d1, self.last_date],
                                    'range': 'max'}})
        d1 = DateTime('2014/05/10')
        d2 = DateTime('2014/06/08')
        renderer.options = {'start': {'query': [d1, d2], 'range': 'minmax'}}
        renderer._fix_range_criteria('start')
        self.assertEqual(renderer.options,
                         {'start': {'query': [d1, self.last_date],
                                    'range': 'minmax'}})


    def test_fix_range_criteria_end(self):
        renderer = self.renderer
        d1 = DateTime('2014/05/20')
        renderer.options = {'end': {'query': d1, 'range': 'max'}}
        renderer._fix_range_criteria('end')
        self.assertEqual(renderer.options,
                         {'end': {'query': [d1, self.first_date],
                                  'range': 'minmax'}})
        d1 = DateTime('2014/05/15')
        renderer.options = {'end': {'query': d1, 'range': 'min'}}
        renderer._fix_range_criteria('end')
        self.assertEqual(renderer.options,
                         {'end': {'query': [d1, self.first_date],
                                  'range': 'min'}})
        d1 = DateTime('2014/02/05')
        d2 = DateTime('2014/05/15')
        renderer.options = {'end': {'query': [d1, d2], 'range': 'minmax'}}
        renderer._fix_range_criteria('end')
        self.assertEqual(renderer.options,
                         {'end': {'query': [d2, self.first_date],
                                  'range': 'minmax'}})


class TestRenderer(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal.portal_types['Topic'].global_allow = True
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal_path = '/'.join(self.portal.getPhysicalPath())
        self.portal.portal_workflow.setChainForPortalTypes(
            ['Folder', 'Event'], ['simple_publication_workflow'])

    def renderer(self, context=None, request=None, view=None,
        manager=None, assignment=None):
        context = context or self.portal
        request = request or self.portal.REQUEST
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager,
                                        name='plone.rightcolumn',
                                        context=self.portal)
        assignment = assignment or calendar.Assignment()

        return getMultiAdapter((context, request, view,
                                manager, assignment), IPortletRenderer)

    def countEventsInPortlet(self, dates):
        weeks = [w for w in dates]
        days = []
        for week in weeks:
            for day in week:
                days.append(day)
        eventsbyday = [len(d['eventslist']) for d in days if d['day'] > 0]
        return sum(eventsbyday)

    def createEvents(self):
        # Create subfolders
        self.portal.invokeFactory('Folder', 'folder1',)
        self.portal.portal_workflow.doActionFor(
                                    self.portal['folder1'], 'publish')
        self.portal.invokeFactory('Folder', 'folder2',)
        self.portal.portal_workflow.doActionFor(
                                    self.portal['folder2'], 'publish')

        # We will add 6 events: 2 on the root folder and 2 on each subfolders
        # Root events
        start, end = self.genDates(delta=0)
        self.portal.invokeFactory('Event', 'e1', startDate=start, endDate=end)
        o = self.portal['e1']
        o.setSubject(['Meeting', ])
        self.portal.portal_workflow.doActionFor(self.portal.e1, 'publish')
        o.reindexObject()
        self.portal.invokeFactory('Event', 'e2', startDate=start, endDate=end)
        o = self.portal['e2']
        o.setSubject(['Workshop', ])
        o.reindexObject()

        # Folder1 events
        start, end = self.genDates(delta=1)
        self.portal.folder1.invokeFactory(
                                'Event', 'e3', startDate=start, endDate=end)
        o = self.portal.folder1['e3']
        o.setSubject(['Meeting', ])
        self.portal.portal_workflow.doActionFor(
                                        self.portal.folder1.e3, 'publish')
        o.reindexObject()
        self.portal.folder1.invokeFactory(
                                'Event', 'e4', startDate=start, endDate=end)
        o = self.portal.folder1['e4']
        o.setSubject(['Workshop', ])
        o.reindexObject()

        # Folder2 events
        start, end = self.genDates(delta=2)
        self.portal.folder2.invokeFactory(
                            'Event', 'e5', startDate=start, endDate=end)
        o = self.portal.folder2['e5']
        o.setSubject(['Party', 'OpenBar', ])
        self.portal.portal_workflow.doActionFor(
                                        self.portal.folder2.e5, 'publish')
        o.reindexObject()

    def createTopicEvents(self):
        # Create subfolders
        self.portal.invokeFactory('Folder', 'folder1',)
        folder1 = self.portal['folder1']
        self.portal.portal_workflow.doActionFor(folder1, 'publish')

        start, end = self.genDates(delta=0)
        folder1.invokeFactory('Event', 'e1', startDate=start, endDate=end)
        self.portal.portal_workflow.doActionFor(folder1.e1, 'publish')
        folder1.e1.reindexObject()
        folder1.invokeFactory('Event', 'e2', startDate=start, endDate=end)
        folder1.e2.reindexObject()

        start, end = self.genDates(delta=2)
        folder1.invokeFactory('Event', 'e3', startDate=start, endDate=end)
        self.portal.portal_workflow.doActionFor(folder1.e3, 'publish')
        folder1.e3.reindexObject()
        start, end = self.genDates(delta=2)
        folder1.invokeFactory('Event', 'e4', startDate=start, endDate=end)
        folder1.e4.reindexObject()

    def createTopic(self):
        self.portal.invokeFactory('Topic', 'example-events',)
        topic = self.portal['example-events']
        type_crit = topic.addCriterion('Type', 'ATPortalTypeCriterion')
        type_crit.setValue(['Event'])

    def createCollection(self):
        self.portal.invokeFactory('Collection', 'example-events',)
        collection = self.portal['example-events']
        collection.setQuery([{'i': 'portal_type',
                              'o': 'plone.app.querystring.operation.selection.is',
                              'v': ['Event']}, ])

    def genDates(self, delta):
        now = DateTime()
        year, month = now.year(), now.month()
        date = DateTime('%s/%s/1' % (year, month))
        hour = 1 / 24.0
        start = date + delta + 23 * hour
        end = date + delta + 23.5 * hour
        return (start, end)

    def test_event_created_last_day_of_month_invalidate_cache(self):
        # First render the calendar portlet when there's no events
        self.portal.REQUEST["ACTUAL_URL"] = self.portal.REQUEST["SERVER_URL"]
        r = self.renderer(assignment=calendar.Assignment())
        html = r.render()

        # Now let's add a new event in the last day of the current month
        year, month = r.getYearAndMonthToDisplay()
        year, month = r.getNextMonth(year, month)
        last_day_month = DateTime('%s/%s/1' % (year, month)) - 1
        hour = 1 / 24.0
        start = last_day_month + 23 * hour
        end = last_day_month + 23.5 * hour
        # Event starts at 23:00 and ends at 23:30
        self.portal.invokeFactory('Event', 'e1', startDate=start, endDate=end)

        # Make sure to publish this event
        self.portal.portal_workflow.doActionFor(self.portal.e1, 'publish')

        # Try to render the calendar portlet again, it must be different now
        r = self.renderer(assignment=calendar.Assignment())
        self.assertNotEqual(html, r.render(), "Cache key wasn't invalidated")

    def testEventsPathSearch(self):
        # Create the events
        self.createEvents()
        # Render a portlet without a root assignment
        path = self.portal_path
        r = self.renderer(assignment=calendar.Assignment())
        r.update()
        self.assertEqual(r.root(), path)
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 5)

        # Render a portlet with a root assignment to folder1
        path = '/folder1'
        r = self.renderer(assignment=calendar.Assignment(root=path))
        r.update()
        self.assertEqual(r.root(), '%s%s' % (self.portal_path, path))
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 2)

        # Render a portlet with a root assignment to folder2
        path = '/folder2'
        r = self.renderer(assignment=calendar.Assignment(root=path))
        r.update()
        self.assertEqual(r.root(), '%s%s' % (self.portal_path, path))
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 1)

    def testEventsTopicSearch(self):
        # Create the events
        self.createTopicEvents()
        # Create the collection
        self.createTopic()
        path = '/example-events'
        r = self.renderer(assignment=calendar.Assignment(root=path,
                          kw=['Foo', ]))
        r.update()

        # kw are ignored and also content type, so published events are
        # returned
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 4)
        # adding a new criteria to the collection change results
        state_crit = self.portal['example-events'].addCriterion(
                                                            'review_state',
                                                            'ATListCriterion')
        state_crit.setValue(['published'])
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 2)

    def testEventsCollectionSearch(self):
        # Create the events
        self.createEvents()
        # Create the collection
        self.createCollection()
        path = '/example-events'
        r = self.renderer(assignment=calendar.Assignment(root=path,
                          kw=['Foo', ]))
        r.update()

        # kw are ignored and also content type, so all event's are returned
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 5)
        # adding a new criteria to the collection change results
        collection = self.portal['example-events']
        new_filter = [{'i': 'review_state',
                       'o': 'plone.app.querystring.operation.selection.is',
                       'v': ['published']}]
        collection.setQuery(collection.getQuery(raw=True) + new_filter)
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 3)

    def testEventsKwSearch(self):
        # Create the events
        self.createEvents()
        # Render a portlet without a root assignment
        path = self.portal_path
        r = self.renderer(assignment=calendar.Assignment())
        r.update()
        self.assertEqual(r.root(), path)
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 5)

        # Render a portlet showing only Meetings
        kw = ['Meeting', ]
        r = self.renderer(assignment=calendar.Assignment(kw=kw))
        r.update()
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 2)

        # Render a portlet showing only Parties
        kw = ['Party', ]
        r = self.renderer(assignment=calendar.Assignment(kw=kw))
        r.update()
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 1)

        # Render a portlet showing Meetings under folder1
        kw = ['Meeting', ]
        path = '/folder1'
        r = self.renderer(assignment=calendar.Assignment(root=path, kw=kw))
        r.update()
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 1)
        self.assertEqual(r.root(), '%s%s' % (self.portal_path, path))

    def testEventsReviewStateSearch(self):
        # Create the events
        self.createEvents()
        # Render a portlet without a root assignment
        path = self.portal_path
        r = self.renderer(assignment=calendar.Assignment())
        r.update()
        self.assertEqual(r.root(), path)
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 5)

        # Render a portlet showing only private events
        review_state = ['private', ]
        r = self.renderer(assignment=calendar.Assignment(review_state=review_state))
        r.update()
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 2)

        # Render a portlet showing published events under folder1
        review_state = ['published', ]
        path = '/folder1'
        r = self.renderer(assignment=calendar.Assignment(root=path, review_state=review_state))
        r.update()
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 1)
        self.assertEqual(r.root(), '%s%s' % (self.portal_path, path))
