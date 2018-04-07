from django.shortcuts import render
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
#from .models import Profile
#from .models import TestCal
#from .models import LoginData
#from .models import IdleFunc
#from .models import ChatFunc
from .models import perData
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json
import time
import datetime

@csrf_exempt
def performance(request):
    inputName = request.GET.get('thename', '') 
    if inputName != '':
        _perF = perData()
        _perF.queue = inputName
        _perF.save()  # save in mysQL
        return HttpResponseRedirect('/')
    performs = perData.objects.all() 
    json_string = json.dumps({"label":"Men", "Not Satisfied":20, "Not Much Satisfied":10, "Satisfied": 50, "Very Satisfied":20})
    render(request, "index.html", {'time_series_json_string': json_string})
    """
    context = {
    'performs' : performs
    }
    return render(request, "index.html", context)
    """

@csrf_exempt
def simple_chart(request):
    plot = figure()
    plot.circle([1,2], [3,4])

    script, div = components(plot, CDN)

    return render(request, "simple_chart.html", {"the_script": script, "the_div": div})
"""
# Create your views here.
@csrf_exempt
def save(request):
    inputName = request.GET.get('thename', '') 
    if inputName != '':
        _newProfile = Profile()
        _newProfile.name = inputName
        _newProfile.save()  # save in mysQL
        return HttpResponseRedirect('/')
    profiles = Profile.objects.all()
    context = {
    'profiles' : profiles
    }
    return render(request, "index.html", context)
    # render

@csrf_exempt
def calc(request):
    inputnumberA = request.GET.get('A', '')
    inputnumberB = request.GET.get('B', '')
    operator = request.GET.get('Operator', '')
    if inputnumberA != '' and inputnumberB != '':
        _newProfile = TestCal()
        _newProfile.numberA = inputnumberA
        _newProfile.numberB = inputnumberB
        _newProfile.operator = operator
        if _newProfile.operator == 'Add' :
            _newProfile.result = float(_newProfile.numberA) + float(_newProfile.numberB);
        elif _newProfile.operator == 'Minus' :
            _newProfile.result = float(_newProfile.numberA) - float(_newProfile.numberB);
        elif _newProfile.operator == 'Multi' :
            _newProfile.result = float(_newProfile.numberA) * float(_newProfile.numberB);
        else :
            _newProfile.result = float(_newProfile.numberA) / float(_newProfile.numberB);
        _newProfile.save()

        return HttpResponseRedirect('/calc')
    testcal = TestCal.objects.all()
    context = {
    'testcals' : testcal
    }
    return render(request, "cal.html", context)
    # render
@csrf_exempt
def login(request):
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
    
        _personalData = LoginData()
        _personalData.user_ID = received_json_data["user_ID"]
        _personalData.password = received_json_data["Password"]
        # check if we've already register
        filterAccount = LoginData.objects.filter(user_ID__iexact = _personalData.user_ID)
        if filterAccount.count() != 0:
            filterPassword = filterAccount.filter(password__iexact = _personalData.password)
            if filterPassword.count() != 0:
                #right
                response_data = {}
                response_data['user_ID'] = _personalData.user_ID
                response_data['Password'] = _personalData.password
                response_data['Exist_or_not'] = 'Right'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                #wrong
                response_data = {}
                response_data['user_ID'] = _personalData.user_ID
                response_data['Password'] = _personalData.password
                response_data['Exist_or_not'] = 'Wrong'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            #new
            _personalData.save()
            response_data = {}
            response_data['user_ID'] = _personalData.user_ID
            response_data['Password'] = _personalData.password
            response_data['Exist_or_not'] = 'New'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    else:
        print "abc"


@csrf_exempt
def idleFunc(request):
    if request.method == "POST":
        received_json_data = json.loads(request.body)

        _personalData = IdleFunc()
        _personalData.ID_me = received_json_data["ID_me"]
        _personalData.Call_ID = received_json_data["Call_ID"]
        _leave = received_json_data["leave"]
        _personalData.time = time.localtime(time.time()).tm_sec

        response_data = {}

        #print _personalData.ID_me
        #print _personalData.Call_ID
        #print _leave
        #print _personalData.time
        
        # ConnectSomeOne, ConnectList, ConnectedId
        # calling otehrs
        if len(_personalData.Call_ID) != 0:
            filterID_toConnect = IdleFunc.objects.filter(ID_me__iexact = _personalData.Call_ID)
            # idle
            if filterID_toConnect.count() != 0:
                # both of them will be busy, delete them from idle list
                t = IdleFunc.objects.get(ID_me__iexact = _personalData.ID_me)
                t.Call_ID = _personalData.Call_ID
                t.save()                                  
                response_data['ConnectSomeOne'] = 'False'
                response_data['ConnectedId'] = _personalData.Call_ID
            else:
                response_data['ConnectSomeOne'] = 'False'
                response_data['ConnectedId'] = ''
            response_data['ConnectList'] = ''
            

        # not calling otehrs, include leaving & idle
        else :
            # leaving
            if _leave == 'True':
                IdleFunc.objects.filter(ID_me__iexact = _personalData.ID_me).delete()
                return 0                                                                        # [help] not sure
                
            # idle, update per second
            elif _leave == 'False':
                filterID_me = IdleFunc.objects.filter(ID_me__iexact = _personalData.ID_me)
                filterID_toBeConnect = IdleFunc.objects.filter(Call_ID__iexact = _personalData.ID_me)
                #print list(filterID_toBeConnect)
                #print filterID_toBeConnect.query

                # exist and someone call
                if filterID_me.count() != 0 and filterID_toBeConnect.count() != 0:
                    response_data['ConnectList'] = ''
                    response_data['ConnectSomeOne'] = 'True'                                     # [help] not sure if json could sent boolean type

                    for e in filterID_toBeConnect:
                        print "calling...",
                        print e.ID_me
                        response_data['ConnectedId'] =  e.ID_me                  
                    filterID_toBeConnect.delete()                       
                    filterID_me.delete()                      

                # nobody call
                else:
                    # first person ID not exist
                    if filterID_me.count() == 0:
                        _personalData.save()   
                        print 'saving data'

                    # exist, but no one call
                    else:
                        ts = IdleFunc.objects.filter(ID_me__iexact = _personalData.ID_me)
                        t = IdleFunc.objects.get(ID_me__iexact = _personalData.ID_me)
                        t.time = _personalData.time
                        t.save()
                    listCon = ''
                    for e in IdleFunc.objects.all():  
                        if(e.ID_me != _personalData.ID_me):                     
                            listCon += (e.ID_me + ' ')
                    print "connect List : ",
                    print listCon
                    response_data['ConnectList'] = listCon
                    response_data['ConnectSomeOne'] = 'False'
                    response_data['ConnectedId'] = ''
            # unexpected error
            else:
                print "unexpected error"

        # update time
        for e in IdleFunc.objects.all():        
            sec = datetime.datetime.now().second
            #print e.time
            eStr = e.time.strftime("%S")
            if (int(sec) - int(eStr) > 1 or int(sec) - int(eStr) < -1) :
                e.delete()
            print 'timeDiffer : ',
            print int(sec)- int(eStr)

                 
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    else:
        print 'abc'
            #print time.mktime(e.timetuple()) + e.microsecond / 1E6


@csrf_exempt
def chatFunc(request):
    if request.method == "POST":
        received_json_data = json.loads(request.body)

        _connectInfo = IdleFunc()       
        _personalData = ChatFunc()      
        _personalData.content = received_json_data["content"]
        _personalData.ID_me = received_json_data["ID_me"]
        #print 'EEE' + str(received_json_data)
        _personalData.Call_ID = received_json_data["Call_ID"]
        print 'I am : ',
        print _personalData.ID_me,
        print 'Call_ID is :',
        print _personalData.Call_ID
        _leave = received_json_data["leave"]
        _personalData.time = time.localtime(time.time()).tm_sec
        response_data = {}


        
        # chatting and waiting
        if _leave == 'False':  
            #print 'wait for chatting'                       
            filterID_meSet = ChatFunc.objects.filter(ID_me__iexact = _personalData.ID_me)
            #filterID_me = get_object_or_404(filterID_meSet, ID_me__iexact = _personalData.ID_me)
            #filterID_me = ChatFunc.objects.get(ID_me__iexact = _personalData.ID_me)
            #filterID_me = filterID_meSet.get(ID_me__iexact = _personalData.ID_me)
            filterCall_IDSet = ChatFunc.objects.filter(ID_me__iexact = _personalData.Call_ID)
            #filterCall_ID = filterCall_IDSet.get(ID_me__iexact = _personalData.Call_ID)
            #print "Do I exist?",
            #print filterID_meSet.count()
            # both are online
            # init            
            if filterID_meSet.count() == 0:
                #print 'count = 0'
                _personalData.save()
                response_data['Content'] = ''
                response_data['ConnectSomeOne'] = 'True'
            # not init
            else:
                if filterCall_IDSet.count() != 0:
                    #print 'count != 0'
                    # Call_ID has content, which will be saved in response_data['Content'] 
                    filterID_me = get_object_or_404(ChatFunc, ID_me__iexact = _personalData.ID_me)
                    filterCall_ID = get_object_or_404(ChatFunc, ID_me__iexact = _personalData.Call_ID)
                    if filterCall_ID.content != '':
                        print 'with content from ',
                        print filterCall_ID.ID_me,
                        print filterCall_ID.content
                        response_data['Content'] = filterCall_ID.content
                        # ID_call reset
                        filterCall_ID.content = ''
                        filterCall_ID.save()
                    else:
                        response_data['Content'] = ''
                        print 'no content now'

                    # if ID_me has message to sent, save it in its database
                    if _personalData.content != '':
                        print 'has message to sent ',
                        print _personalData.content
                        filterID_me.content = _personalData.content
                        filterID_me.save()

                    # update time
                    filterID_me.time = _personalData.time
                    filterID_me.save()

                    for e in ChatFunc.objects.all():        
                        sec = datetime.datetime.now().second
                        #print e.time
                        eStr = e.time.strftime("%S")
                        if (int(sec) - int(eStr) > 2 or int(sec) - int(eStr) < -2) :
                            e.delete()
                        #print 'timeDiffer : ',
                        #print int(sec)- int(eStr)

                    response_data['ConnectSomeOne'] = 'True'
                
                # he/she is offline 
                else:   
                    print 'offline'
                    response_data['Content'] = ''
                    response_data['ConnectSomeOne'] = 'False'
                    # append ID_me in idle database and delete ID_me in chat database
                    _connectInfo.ID_me = _personalData.ID_me
                    _connectInfo.save()
                    ChatFunc.objects.filter(ID_me__iexact = _personalData.ID_me).delete()

    
        # leaving      
        else:
            # append two ID in idle database and delete two ID in chat database
            _connectInfo.ID_me = _personalData.ID_me
            _connectInfo.save()
            _connectInfo.ID_me = _personalData.Call_ID
            _connectInfo.save()  
            ChatFunc.objects.filter(ID_me__iexact = _personalData.ID_me).delete()
            ChatFunc.objects.filter(ID_me__iexact = _personalData.Call_ID).delete()        
            return 0
        
        return HttpResponse(json.dumps(response_data), content_type="application/json")

        
    else:
        print 'abc'
"""
