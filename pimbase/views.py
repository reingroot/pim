from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext
from pimbase.models import *
from pimbase.forms import UserForm
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.db.models import Count
import datetime

class FilterData:
    def __init__(self, request, definition):
        self.definition = definition
        self.request = request
    def is_more(self):
        self.request.session.setdefault('%s_more' % (self.definition.name, ), False)
        return self.request.session['%s_more' % (self.definition.name, )]
    def is_selected(self):
        self.request.session.setdefault('%s' % (self.definition.name, ), None)

        return self.request.session['%s' % (self.definition.name, )] != None 
    def get_selected(self):
        self.request.session.setdefault('%s' % (self.definition.name, ), None)

        return self.request.session['%s' % (self.definition.name, )]

class FilterDefinition:
    def __init__(self, name, model, title, attr):
        self.name = name
        self.model = model
        self.title = title
        self.attr = attr
    def show_more(self, request):
        request.session['%s_more' % (self.name, )] = True

        return HttpResponseRedirect(reverse('pimbase.views.index'))
    def show_less(self, request):
        request.session['%s_more' % (self.name, )] = False

        return HttpResponseRedirect(reverse('pimbase.views.index'))
    def set_filter(self, request, param):
        try:
            id = int(param)
        except (ValueError, TypeError):
            return HttpResponseServerError("Invalid parameter")

        if not self.model.objects.filter(pk=id):
            return HttpResponseServerError("Object doesn't exist")

        request.session['%s' % (self.name, )] = id

        return HttpResponseRedirect(reverse('pimbase.views.index'))
    def unset_filter(self, request):
        del request.session['%s' % (self.name, )]

        return HttpResponseRedirect(reverse('pimbase.views.index'))
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urlpatterns = patterns('',
            url('show_more_%s' % (self.name, ), self.show_more),
            url('show_less_%s' % (self.name, ), self.show_less),
            url('set_%s/(?P<param>\d+)' % (self.name, ), self.set_filter),
            url('unset_%s' % (self.name, ), self.unset_filter),
        )

        return urlpatterns
    @property
    def urls(self):
        return self.get_urls()

class FilterManager:
    def __init__(self):
        self.registry = []
    def register(self, filter):
        self.registry.append(filter)
    def get_filterdata(self, request):
        l = []
        for r in self.registry:
            l.append(FilterData(request, r))

        return l
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include

        urlpatterns = patterns('')

        for f in self.registry:
            # XXX: prolly a better way to do this.
            urlpatterns += patterns('', url('', include(f.urls)) )

        return urlpatterns

    @property
    def urls(self):
        return self.get_urls()

fm = FilterManager()
fm.register(FilterDefinition('citizenrole', CitizenRole, 'afhankelijk van je situatie', 'label'))

# Disable these options temporarily since they aren't used with te current dataset.
#fm.register(FilterDefinition('organisationtype', OrganisationType, 'op type', 'name'))
#fm.register(FilterDefinition('sector', Sector, 'op sector', 'name'))
#fm.register(FilterDefinition('collectedinformation', CollectedInformation, 'op wat ze mogelijk van je weten', 'name'))

def search(query, fm):
    """ Search for specific organisationtype, sector or role. """
    
    org_list = Organisation.objects.all()

    for f in fm:
        if f.is_selected():
            filter_context = {
                '%s' % (f.definition.name, ): f.get_selected(),
            }
            org_list = org_list.filter(**filter_context)

    if query:
        org_list = org_list.filter(name__icontains = query)

    return org_list

def index(request):
    # initialize the session
    request.session.setdefault('companies', [])

    # URL processing
    page_id = 1
    if 'p' in request.GET.keys():
        try:
            page_id = int(request.GET.get('p', ''))
        except (ValueError, TypeError):
            return HttpResponseServerError("Invalid parameter")
    query = request.GET.get('q', '')

    selected_companies = Organisation.objects.filter(pk__in = request.session['companies'])
    org_list = search(query, fm.get_filterdata(request))
    org_count = org_list.count()
    paginator = Paginator(org_list, 30)

    try:
        org = paginator.page(page_id)
    except (EmptyPage, InvalidPage):
        # Shouldn't this just raise a 404?
        return HttpResponseServerError("Page doesn't exist")

    # Based on the Yahoo search pagination pattern:
    # http://developer.yahoo.com/ypatterns/navigation/pagination/search.html
    # XXX: make the numbers less mystical.
    if org.number > 4:
        search_range = range(org.number - 3, min(3 + org.number, org.paginator.num_pages))
    else:
        search_range = range(1, min(7, org.paginator.num_pages + 1))

    context = {
        'query': query,
        'fm': fm.get_filterdata(request),
        'org_count': org_count,
        'organisations': org,
        'selected_companies': selected_companies,
        'search_range': search_range,
    }

    return render_to_response('pim/index.html', context,
        context_instance=RequestContext(request))

def cleancompanylist(request):
    request.session['companies'] = []
    request.session.modified = True

    return HttpResponseRedirect(reverse('pimbase.views.index'))

def addcompany(request, param):
    company = request.session.setdefault('companies', [])
    try:
        company_id = int(param)
    except (ValueError, TypeError):
        return HttpResponseServerError("Invalid parameter")

    if not Organisation.objects.filter(pk=company_id):
        return HttpResponseServerError("Object doesn't exist")

    if company_id not in request.session['companies']:
        request.session['companies'].append(company_id)
        request.session.modified = True

    return HttpResponseRedirect(reverse('pimbase.views.index'))

def delcompany(request, param):
    request.session.setdefault('companies', [])

    try:
        company_id = int(param)
    except (ValueError, TypeError):
        return HttpResponseServerError("Invalid parameter")

    request.session['companies'].remove(company_id)
    request.session.modified = True

    return HttpResponseRedirect(reverse('pimbase.views.index'))

def userdata(request):
    request.session.setdefault('companies', [])
    if len(request.session['companies']) == 0:
        return HttpResponseServerError("No companies selected")
    selected_companies = Organisation.objects.filter(pk__in = request.session['companies'])

    if request.method == 'POST':
        form = UserForm(request, request.POST)
        if form.is_valid():
            # TODO: We might consider a neat Class wrapper for the
            # user data - for both generality and oversight. This class
            # could later be extended to hold it's data in some other form
            # and can be extended with smart functionality.
            #
            # It could essentially be a Django model which is never saved.
            # This would give us access to all the database's relational
            # stuff and will make it a lot easier to provide for
            # (optional and anonymous) user feedback later.
            #
            # Furthermore: a 'standardized' way of storing this data
            # might add some oversight to what data is kept, where and
            # how.
            request.session['firstname'] = form.cleaned_data['firstname']
            request.session['lastname'] = form.cleaned_data['lastname']
            request.session['street_address'] = form.cleaned_data['street_address']
            request.session['postcode'] = form.cleaned_data['postcode']
            request.session['city'] = form.cleaned_data['city']

            ids = Identifier.objects.filter(organisation__in = request.session['companies'])

            misc = []
            for i in ids:
                if 'misc_%d' % (i.pk, ) in form.cleaned_data.keys():
                    misc.append((i, form.cleaned_data['misc_%d' % (i.pk, )]))

            request.session['misc'] = misc
            request.session.modified = True

            return HttpResponseRedirect(reverse('pimbase.views.generate'))
    else:
        form = UserForm(request)

    context = {
        'form': form,
        'selected_companies': selected_companies
    }

    return render_to_response('pim/userdata.html', context,
        context_instance=RequestContext(request))

def generate(request):
    request.session.setdefault('companies', [])
    if len(request.session['companies']) == 0:
        return HttpResponseServerError("No companies selected")
    selected_companies = Organisation.objects.filter(pk__in = request.session['companies'])

    return render_to_response('pim/generate.html', {'selected_companies': selected_companies},
        context_instance=RequestContext(request))

def generatehtml(request, param):
    request.session.setdefault('companies', [])
    if len(request.session['companies']) == 0:
        return HttpResponseServerError("No companies selected")

    try:
        company_id = int(param)
    except (ValueError, TypeError):
        return HttpResponseServerError("Invalid parameter")

    if company_id not in request.session['companies']:
        return HttpResponseServerError("Object doesn't exist")

    required_keys = (
        'firstname',
        'lastname',
        'street_address',
        'postcode',
        'city'
    )
    # <= means issubset
    if required_keys <= request.session.keys():
        return HttpResponseServerError("Invalid parameters")

    try:
        organisation = Organisation.objects.get(pk=company_id)
    except Organisation.DoesNotExist:
        return HttpResponseServerError("Object doesn't exist")

    context = {
        'organisation': organisation,
        'firstname': request.session['firstname'],
        'lastname': request.session['lastname'],
        'street_address': request.session['street_address'],
        'postcode': request.session['postcode'],
        'city': request.session['city'],
        'misc': request.session['misc'],
        'currentdate': datetime.date.today(),
    }

    return render_to_response('pim/generatehtml.html', context)
