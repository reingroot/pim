from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext
from models import City, Organisation, Keyword
from forms import AddCompanyForm, UserForm

from reportlab.pdfgen import canvas
from django.http import HttpResponse

def search(request):
	org_list = Organisation.objects.all()

	city_ids = request.session['cities']
	if len(city_ids) > 0:
		org_list = org_list.filter(city__in = city_ids)

	keyword_ids = request.session['keywords']
	if len(keyword_ids) > 0:
		org_list = org_list.filter(keyword__in = keyword_ids)

	return org_list

def index(request, param = None):
	# initialize the session
	request.session.setdefault('cities', [])
	request.session.setdefault('companies', [])
	request.session.setdefault('keywords', [])

	# URL processing
	page_id = 1
	if param != None:
		try:
			page_id = int(param)
		except (ValueError, TypeError):
			return HttpResponse("fail")

	# Form processing
	if request.method == 'POST':
		form = AddCompanyForm(request.POST)
		if form.is_valid():
			companies = [comp.pk for comp in form.cleaned_data['companies']]
			for pk in companies:
				if pk not in request.session['companies']:
					request.session['companies'].append(pk)
					request.session.modified = True
			return HttpResponseRedirect('/letter/')
	else:
		form = AddCompanyForm()


	cities = City.objects.all()
	keywords = Keyword.objects.all()
	selected_cities = City.objects.filter(pk__in = request.session['cities'])
	selected_keywords = Keyword.objects.filter(pk__in = request.session['keywords'])
	selected_companies = Organisation.objects.filter(pk__in = request.session['companies'])
	org_list = search(request)
	org_count = org_list.count()
	paginator = Paginator(org_list, 10)

	try:
		org = paginator.page(page_id)
	except (EmptyPage, InvalidPage):
		return HttpResponse("fail")

	return render_to_response('index.html',
		{
		'cities': cities,
		'form': form,
		'keywords': keywords,
		'org_count': org_count,
		'organisations': org,
		'selected_cities': selected_cities,
		'selected_companies': selected_companies,
		'selected_keywords': selected_keywords,
		},
		context_instance=RequestContext(request))

def delcompany(request, param):
	request.session.setdefault('companies', [])

	try:
		company_id = int(param)
	except (ValueError, TypeError):
		return HttpResponse("fail")

	request.session['companies'].remove(company_id)
	request.session.modified = True

	return HttpResponseRedirect('/letter/')

def addcity(request, param):
	cities = request.session.setdefault('cities', [])
	try:
		city_id = int(param)
	except (ValueError, TypeError):
		return HttpResponse("fail")

	if not City.objects.filter(pk=city_id):
		return HttpResponse("fail")

	if city_id not in request.session['cities']:
		request.session['cities'].append(city_id)
		request.session.modified = True
	return HttpResponseRedirect('/letter/')

def delcity(request, param):
	request.session.setdefault('cities', [])

	try:
		city_id = int(param)
	except (ValueError, TypeError):
		return HttpResponse("fail")

	request.session['cities'].remove(city_id)
	request.session.modified = True

	return HttpResponseRedirect('/letter/')

def addkeyword(request, param):
	request.session.setdefault('keywords', [])

	try:
		keyword_id = int(param)
	except (ValueError, TypeError):
		return HttpResponse("fail")

	if not Keyword.objects.filter(pk=keyword_id):
		return HttpResponse("fail")

	if keyword_id not in request.session['keywords']:
		request.session['keywords'].append(keyword_id)
		request.session.modified = True
	return HttpResponseRedirect('/letter/')

def delkeyword(request, param):
	request.session.setdefault('keywords', [])

	try:
		keyword_id = int(param)
	except (ValueError, TypeError):
		return HttpResponse("fail")

	request.session['keywords'].remove(keyword_id)
	request.session.modified = True

	return HttpResponseRedirect('/letter/')

def userdata(request):
	if request.method == 'POST': # If the form has been submitted...
		form = UserForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			request.session['firstname'] = form.cleaned_data['firstname']
			request.session['lastname'] = form.cleaned_data['lastname']
			request.session['street_address'] = form.cleaned_data['street_address']
			request.session['postcode'] = form.cleaned_data['postcode']
			request.session['city'] = form.cleaned_data['city']
			return HttpResponseRedirect('/letter/generate') # Redirect after POST
	else:
		form = UserForm() # An unbound form

	return render_to_response('userdata.html', {'form': form,},
		context_instance=RequestContext(request))

def generate(request):
	request.session.setdefault('companies', [])
	selected_companies = Organisation.objects.filter(pk__in = request.session['companies'])

	return render_to_response('generate.html', {'selected_companies': selected_companies})

def generatepdf(request, param):
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(mimetype='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=somefilename.pdf'

	# Create the PDF object, using the response object as its "file."
	p = canvas.Canvas(response)

	# Draw things on the PDF. Here's where the PDF generation happens.
	# See the ReportLab documentation for the full list of functionality.
	p.drawString(100, 100, "Hello world.")

	# Close the PDF object cleanly, and we're done.
	p.showPage()
	p.save()
	return response
