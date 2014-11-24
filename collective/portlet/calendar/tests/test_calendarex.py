import unittest2 as unittest

from zope.component import getUtility, getMultiAdapter

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from Products.GenericSetup.utils import _getDottedName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from DateTime import DateTime
from collective.portlet.calendar import calendar

from collective.portlet.calendar.testing import INTEGRATION_TESTING


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

        # We will add 3 events. On the root folder and on each subfolder
        # Root event
        start, end = self.genDates(delta=0)
        self.portal.invokeFactory('Event', 'e1', startDate=start, endDate=end)
        o = self.portal['e1']
        o.setSubject(['Meeting', ])
        o.reindexObject()
        self.portal.portal_workflow.doActionFor(self.portal.e1, 'publish')

        # Folder1 event
        start, end = self.genDates(delta=1)
        self.portal.folder1.invokeFactory(
                                'Event', 'e2', startDate=start, endDate=end)
        o = self.portal.folder1['e2']
        o.setSubject(['Meeting', ])
        o.reindexObject()
        self.portal.portal_workflow.doActionFor(
                                        self.portal.folder1.e2, 'publish')

        # Folder2 event
        start, end = self.genDates(delta=2)
        self.portal.folder2.invokeFactory(
                            'Event', 'e3', startDate=start, endDate=end)
        o = self.portal.folder2['e3']
        o.setSubject(['Party', 'OpenBar', ])
        o.reindexObject()
        self.portal.portal_workflow.doActionFor(
                                        self.portal.folder2.e3, 'publish')

    def createTopicEvents(self):
        # Create subfolders
        self.portal.invokeFactory('Folder', 'folder1',)
        folder1 = self.portal['folder1']
        self.portal.portal_workflow.doActionFor(folder1, 'publish')

        start, end = self.genDates(delta=0)
        folder1.invokeFactory('Event', 'e1', startDate=start, endDate=end)
        folder1.e1.reindexObject()
        self.portal.portal_workflow.doActionFor(folder1.e1, 'publish')

        start, end = self.genDates(delta=2)
        folder1.invokeFactory('Event', 'e2', startDate=start, endDate=end)
        folder1.e2.reindexObject()

    def createTopic(self):
        self.portal.invokeFactory('Topic', 'example-events',)
        topic = self.portal['example-events']
        type_crit = topic.addCriterion('Type', 'ATPortalTypeCriterion')
        type_crit.setValue(['Event'])

    def createCollection(self):
        self.portal.invokeFactory('Collection', 'example-events',)
        collection = self.portal['example-events']
        collection.setQuery([{'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['Event']}, ])

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
                    self.countEventsInPortlet(r.getEventsForCalendar()), 3)

        # Render a portlet with a root assignment to folder1
        path = '/folder1'
        r = self.renderer(assignment=calendar.Assignment(root=path))
        r.update()
        self.assertEqual(r.root(), '%s%s' % (self.portal_path, path))
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 1)

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

        # kw are ignored and also content type, so all events are displayed
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 2)
        # adding a new criteria to the collection change results
        state_crit = self.portal['example-events'].addCriterion(
                                                            'review_state',
                                                            'ATListCriterion')
        state_crit.setValue(['private', ])
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 1)

    def testEventsCollectionSearch(self):
        # Create the events
        self.createTopicEvents()
        # Create the collection
        self.createCollection()
        path = '/example-events'
        r = self.renderer(assignment=calendar.Assignment(root=path,
                          kw=['Foo', ]))
        r.update()

        # kw are ignored and also content type, so all events are displayed
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 2)
        # adding a new criteria to the collection change results
        collection = self.portal['example-events']
        new_filter = [{'i': 'review_state', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['private']}]
        collection.setQuery(collection.getQuery(raw=True) + new_filter)
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 1)

    def testEventsKwSearch(self):
        # Create the events
        self.createEvents()
        # Render a portlet without a root assignment
        path = '%s' % self.portal_path
        r = self.renderer(assignment=calendar.Assignment())
        r.update()
        self.assertEqual(r.root(), path)
        self.assertEqual(
                    self.countEventsInPortlet(r.getEventsForCalendar()), 3)

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
