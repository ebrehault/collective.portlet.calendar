from zope.component import getUtility, getMultiAdapter
from zope.site.hooks import setHooks, setSite

from Products.GenericSetup.utils import _getDottedName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from DateTime import DateTime
from collective.portlet.calendar import calendar
from plone.app.portlets.tests.base import PortletsTestCase

class TestPortlet(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        self.setRoles(('Manager',))

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
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        
        addview.createAndAdd(data={'name':'My Calendar',
                                   'root':u''})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], calendar.Assignment))

    def testPortletProperties(self):
        portlet = getUtility(IPortletType, name='portlets.CalendarEx')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={'name':'My Calendar',
                                   'root':u''})
        title = mapping.values()[0].title
        root = mapping.values()[0].root
        self.assertEqual(title,'My Calendar')
        self.assertEqual(root, u'')
        

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = calendar.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, calendar.Renderer))


class TestRenderer(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        self.portal_path = '/'.join(self.portal.getPhysicalPath())

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or calendar.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
    
    def countEventsInPortlet(self,dates):
        weeks = [w for w in dates]
        days = []
        for week in weeks:
            for day in week:
                days.append(day)
        eventsbyday = [len(d['eventslist']) for d in days if d['day']>0]
        return sum(eventsbyday)
    
    def createEvents(self):
        p = self.portal
        self.setRoles(('Manager',))
        # Create subfolders
        p.invokeFactory('Folder', 'folder1',)
        p.portal_workflow.doActionFor(p.folder1, 'publish')
        p.invokeFactory('Folder', 'folder2',)
        p.portal_workflow.doActionFor(p.folder2, 'publish')
        
        # We will add 3 events. On the root folder and on each subfolder
        # Root event
        start,end = self.genDates(delta=0)
        p.invokeFactory('Event','e1', startDate=start, endDate=end)
        o = p['e1']
        o.setSubject(['Meeting',])
        o.reindexObject()
        p.portal_workflow.doActionFor(p.e1,'publish')
        
        # Folder1 event
        start,end = self.genDates(delta=1)
        p.folder1.invokeFactory('Event','e2', startDate=start, endDate=end)
        o = p.folder1['e2']
        o.setSubject(['Meeting',])
        o.reindexObject()
        p.portal_workflow.doActionFor(p.folder1.e2,'publish')
        
        # Folder2 event
        start,end = self.genDates(delta=2)
        p.folder2.invokeFactory('Event','e3', startDate=start, endDate=end)
        o = p.folder2['e3']
        o.setSubject(['Party','OpenBar',])
        o.reindexObject()
        p.portal_workflow.doActionFor(p.folder2.e3,'publish')
    
    def createTopicEvents(self):
        p = self.portal
        self.setRoles(('Manager',))
        # Create subfolders
        p.invokeFactory('Folder', 'folder1',)
        folder1 = p['folder1']
        p.portal_workflow.doActionFor(folder1,'publish')
        start, end = self.genDates(delta=0)
        folder1.invokeFactory('Event','e1', startDate=start, endDate=end)
        start, end = self.genDates(delta=2)
        p.portal_workflow.doActionFor(folder1.e1, 'publish')
        folder1.invokeFactory('Event','e2', startDate=start, endDate=end)
    
    def createTopic(self):
        p = self.portal
        self.setRoles(('Manager',))
        p.invokeFactory('Topic', 'example-events',)
        topic = p['example-events']
        type_crit = topic.addCriterion('Type','ATPortalTypeCriterion')
        type_crit.setValue(['Event'])
    
    def genDates(self,delta):
        now = DateTime()
        year, month = now.year(),now.month()
        date = DateTime('%s/%s/1' % (year, month))
        hour = 1 / 24.0
        start = date + delta + 23*hour
        end = date + delta + 23.5*hour
        return (start,end)
    
    def test_event_created_last_day_of_month_invalidate_cache(self):
        # First render the calendar portlet when there's no events
        r = self.renderer(assignment=calendar.Assignment())
        html = r.render()

        # Now let's add a new event in the last day of the current month
        year, month = r.getYearAndMonthToDisplay()
        year, month = r.getNextMonth(year, month)
        last_day_month = DateTime('%s/%s/1' % (year, month)) - 1
        hour = 1 / 24.0
        start = last_day_month + 23*hour
        end = last_day_month + 23.5*hour
        self.setRoles(('Manager',))
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
        self.assertEqual(self.countEventsInPortlet(r.getEventsForCalendar()),3)
        
        # Render a portlet with a root assignment to folder1
        path = '/folder1'
        r = self.renderer(assignment=calendar.Assignment(root=path))
        r.update()
        self.assertEqual(r.root(), '%s%s' % (self.portal_path, path))
        self.assertEqual(self.countEventsInPortlet(r.getEventsForCalendar()),1)
        
        # Render a portlet with a root assignment to folder2
        path = '/folder2'
        r = self.renderer(assignment=calendar.Assignment(root=path))
        r.update()
        self.assertEqual(r.root(), '%s%s' % (self.portal_path, path))
        self.assertEqual(self.countEventsInPortlet(r.getEventsForCalendar()),1)
        
    def testEventsCollectionSearch(self):
        # Create the events
        self.createTopicEvents()
        # Create the collection
        self.createTopic()
        path = '/example-events'
        r = self.renderer(assignment=calendar.Assignment(root=path, kw=['Foo',]))
        r.update()
        # kw are ignored and also content type, so all events are displayed
        self.assertEqual(self.countEventsInPortlet(r.getEventsForCalendar()), 2)
        # adding a new criteria to the collection change results
        state_crit = self.portal['example-events'].addCriterion('review_state', 'ATListCriterion')
        state_crit.setValue(['private',])
        self.assertEqual(self.countEventsInPortlet(r.getEventsForCalendar()), 1)

    def testEventsKwSearch(self):
        # Create the events
        self.createEvents()
        # Render a portlet without a root assignment
        path = '%s' % self.portal_path
        r = self.renderer(assignment=calendar.Assignment())
        r.update()
        self.assertEqual(r.root(), path)
        self.assertEqual(self.countEventsInPortlet(r.getEventsForCalendar()),3)
        
        # Render a portlet showing only Meetings
        kw = ['Meeting',]
        r = self.renderer(assignment=calendar.Assignment(kw=kw))
        r.update()
        self.assertEqual(self.countEventsInPortlet(r.getEventsForCalendar()),2)
        
        # Render a portlet showing only Parties
        kw = ['Party',]
        r = self.renderer(assignment=calendar.Assignment(kw=kw))
        r.update()
        self.assertEqual(self.countEventsInPortlet(r.getEventsForCalendar()),1)
        
        # Render a portlet showing Meetings under folder1
        kw = ['Meeting',]
        path = '/folder1'
        r = self.renderer(assignment=calendar.Assignment(root=path, kw=kw))
        r.update()
        self.assertEqual(self.countEventsInPortlet(r.getEventsForCalendar()),1)
        self.assertEqual(r.root(),'%s%s' % (self.portal_path, path))
    

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
