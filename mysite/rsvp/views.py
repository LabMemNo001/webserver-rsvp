from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from rsvp.forms import RegistrationForm, EventForm, OwnerForm, AddUserForm, AcceptUserForm, QuestionForm, ChoiceForm, AddVendorForm, EssayForm, AdduserForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from rsvp.models import Event, Question, Choice, Answer
from django.forms import formset_factory
from django.core.mail import EmailMultiAlternatives
# Create your views here.


def send_email(recevier, text, html):
    subject, from_email, to = 'Message From RSVP System','ys206@vcm-152.vm.duke.edu',recevier
    text_content = text
    html_content = html
    msg = EmailMultiAlternatives(subject, text_content, from_email,[to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def get_questionsheet(event, request):
    if request not in event.owner.all():
       if request not in event.vendor.all():
           return None
       else:
           question = Question.objects.filter(event_belong = event, vendor = request)
    else:
        question = Question.objects.filter(event_belong = event)
    questionsheet = {}
    for i in question:
        if i.multi:
            c= Choice.objects.filter(question = i)
            questionsheet[i] = c
        else:
            questionsheet[i]=None
    return questionsheet

def get_answersheet(event, request, user, guest):
    if request in event.vendor.all():
        question = Question.objects.filter(event_belong = event, vendor = request)
    if request in (event.owner.all() or event.guest.all()):
        question = Question.objects.filter(event_belong = event)
    answersheet = {}
    done = False
    for q in question:
        if Answer.objects.filter(question = q, user = user, guest = guest):
            done = True
            answer = Answer.objects.get(question = q, user = user,guest = guest)
            if q.multi:
                answersheet[q] = Choice.objects.get(pk = answer.answer_text).choice_text
            else:
                answersheet[q] = answer.answer_text
        else:
            answersheet[q] = 'Not Finished!'
    if done or not guest:
        return answersheet
    else:
        return None


def home(request):
    return render(request, 'rsvp/home.html')


def register(request):
    if request.method=='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = RegistrationForm();
        
    args = {'form': form}
    return render(request, 'rsvp/reg_form.html', args)


def guest_value(guest_val):
    if guest_val is 0:
        guest = False
    elif guest_val is 1:
        guest = True
    else:
        raise Http404("Page Not Found")
    return guest


@login_required
def add_user(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    if event not in request.user.owner.all():
        raise Http404("Event does not exist")
    if request.method=='POST':
        form = AdduserForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data['email']
            identity = form.cleaned_data['identity']
            invited = User.objects.filter(email = email)
            host = request.get_host()
            if invited:
                for i in invited:
                    if identity == 'owner':
                        event.owner.add(i)
                    if identity == 'vendor':
                        event.vendor.add(i)
                    if identity == 'guest':
                        event.invite.add(i)
                    text = 'Invite to Join the Event %s!'%event.event_name
                    html = u'Dear sir or madam:<br>You are invited as {},please login and check!<a href = "http://{}">Click to Login<a>'.format(identity,host)
                    send_email(i.email,text,html)
            else:
                text = 'Invite to Join the Event %s!'%event.event_name
                html = u'Dear sir or madam:<br>You are invited as {},please register to receive the initation!<br><a href = "http://{}/rsvp/register">Click to Register<a>'.format(identity, host)
                send_email(email,text,html)
            return redirect('/rsvp/profile')
    else:
        form = AdduserForm(request.POST or None)
    args = {'form': form, 'event':event}
    return render(request, 'rsvp/add_user.html', args)


@login_required
def accept_invite(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    if request.method=='POST':
        event.invite.remove(request.user)
        event.guest.add(request.user)
        return redirect('/rsvp/profile')

    return render(request, 'rsvp/accept_invite.html', )




@login_required
def add_event(request):
    if request.method=='POST':
        form = EventForm(request.POST)
        if form.is_valid(): 
          event_name = form.cleaned_data['event_name']
          event_content = form.cleaned_data['event_content']
          event = Event(event_name = event_name, event_content = event_content)
          event.save()
          event.owner.add(request.user)   
          return redirect('../profile')
    else:
        form = EventForm();
    return render(request, 'rsvp/add_event.html', {'form': form})
          

@login_required
def event_edit(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method=='POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid(): 
            form.save()
            return redirect('/rsvp/profile')
    else:
        form = EventForm(instance=event);
    return render(request, 'rsvp/event_edit.html', {'form': form})
    


@login_required
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/rsvp/logout/")
    
    
@login_required
def edit_profile(request):
    if request.method=='POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/rsvp/profile')
    else:
        form = UserChangeForm(instance=request.user)
        args = {'form': form}
        return render(request, 'rsvp/edit_profile.html', args)
        

@login_required
def index(request, event_id, guest_val):
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    todo_list = []
    fin_list = []
    question = Question.objects.filter(event_belong = event)
    guest = guest_value(guest_val)
    for q in question:
        if Answer.objects.filter(question = q, user = request.user, guest = guest):
            fin_list.append(q)
        else:
            todo_list.append(q)
    args = {'todo_list': todo_list,'fin_list': fin_list, 'event': event, 'guest_val': guest_val}
    return render(request, 'rsvp/index.html', args)
    
    
@login_required
def question_detail(request, question_id, event_id, guest_val):
    event = get_object_or_404(Event, pk=event_id)
    question_list = event.question_set.all()
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'rsvp/detail.html', {'guest_val':guest_val, 'question': question, 'event':event})

@login_required
def question_essay(request, question_id, event_id, guest_val):
    event = get_object_or_404(Event, pk=event_id)
    question = get_object_or_404(Question, pk=question_id)
    if request.user not in event.guest.all():
        raise Http404("Page Not Found")
    guest = guest_value(guest_val) 
    form = EssayForm()
    if question.expired is True:
        context = "The question you chose is already expired!"
        todo_list = []
        fin_list = []
        question = Question.objects.filter(event_belong = event)
        for q in question:
            if Answer.objects.filter(question = q, user = request.user):
                fin_list.append(q)
            else:
                todo_list.append(q)
        args = {'todo_list': todo_list,'fin_list': fin_list, 'event': event, 'context':context}
        return render(request, 'rsvp/index.html', args)
    if request.method == 'POST':
        form = EssayForm(request.POST or None)
        if form.is_valid():
            if Answer.objects.filter(question = question,user = request.user,guest = guest):
                answer = Answer.objects.get(question = question,user = request.user,guest = guest)
                answer.answer_text = form.cleaned_data['answer']
            else:
                answer = Answer(question = question,
                                user = request.user,
                                answer_text = form.cleaned_data['answer'],
                                guest = guest,
                )
            answer.save()
        return HttpResponseRedirect('/rsvp/{}/{}/question_index'.format(event_id,guest_val))
    else:
         if Answer.objects.filter(question = question,user = request.user,guest =guest):
             answer = Answer.objects.get(question = question,user = request.user,guest = guest)
             form.initial={'answer': answer.answer_text }
    return render(request, 'rsvp/answeressay.html'.format(event_id,guest_val), {
        'question': question,
        'event': event,
        'form':form,
    })

@login_required
def question_vote(request, question_id, event_id, guest_val):
    event = get_object_or_404(Event, pk=event_id)
    question = get_object_or_404(Question, pk=question_id)
    if request.user not in event.guest.all():
        raise Http404("Page Not Found")
    guest = guest_value(guest_val)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'rsvp/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
            'event': event,
        })
    else:
        if Answer.objects.filter(question = question,user = request.user,guest = guest):
            answer = Answer.objects.get(question = question,user = request.user,guest = guest)
            answer.answer_text = str(selected_choice.pk)
        else:
            answer = Answer(question = question,
                            user = request.user,
                            answer_text = selected_choice.pk,guest = guest)
        answer.save()
        return HttpResponseRedirect('/rsvp/{}/{}/question_index'.format(event_id,guest_val))  


@login_required
def answer_detail(request,event_id):
    event = get_object_or_404(Event, pk=event_id)
    answersheet = get_answersheet(event,request.user,request.user,False)
    return render(request, 'rsvp/answer_detail.html',{'event_id':event_id,'answersheet':answersheet})  

    
@login_required
def question_create(request, event_id):
    try:
        event = Event.objects.get(pk = event_id)
    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    if request.COOKIES.get('extra'):
        extra = int(request.COOKIES.get('extra'))
    else:
        extra = 0
    if request.method == 'POST':
        question = QuestionForm(request.POST or None)
        vendor = AddVendorForm(request.POST or None, instance = event)
        vendor.fields["vendor"].queryset = event.vendor.all()
        if request.POST.get('sub'):
            if question.is_valid():
                q = Question(name = question.cleaned_data['name'],event_belong=event,multi = False)
                q.save()
                if vendor.is_valid():
                    v = vendor.cleaned_data['vendor']
                    for i in v:
                        q.vendor.add(i)
                    q.save()
                choice = ChoiceForm(request.POST,extra = extra)
                for i in range(0,extra):
                    if request.POST['choice_%i'%i]:
                        c  = Choice(choice_text=request.POST['choice_%i'%i], question = q,votes = 0)
                        c.save()
                        q.multi = True
                        q.save()
                

            response = redirect('/rsvp/profile')
            response.delete_cookie('extra')
            return response
        else:
            if request.POST.get('add'):        
                extra += 1
            if request.POST.get('del'):
                if extra>1:
                    extra -= 1 
            choice = ChoiceForm(request.POST or None, extra = extra)
    else:
        extra = 0
        question = QuestionForm(request.POST or None)
        vendor = AddVendorForm(request.POST or None)
        vendor.fields["vendor"].queryset = event.vendor.all()
        choice = ChoiceForm(request.POST or None, extra = extra)        
    response = render(request,'rsvp/question.html',{'question':question,'vendor':vendor,'choice':choice},)
    response.set_cookie('extra',extra)
    return response
    

    
@login_required
def event_detail(request,event_id):
    try:
        event = Event.objects.get(pk = event_id)
    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    guest = event.guest.all();
    if request.method == "POST":
        host = request.get_host()
        q = Question.objects.filter(event_belong = event)
        for i in q:
            if request.POST.get(str(i.pk)):
                text = 'Question is Deleted!%s!'%event.event_name
                html = u'Dear sir or madam:<br>The Question {} is deleted!,please login and check!<a href = "http://{}">Click to Login<a>'.format(Question.objects.get(pk = i.pk).name, host)                
                Question.objects.filter(pk = i.pk).delete()
                guest = event.guest.all()
                for g in guest:             
                    send_email(g.email,text,html)
                break
    q = Question.objects.filter(event_belong = event)
    questionsheet = get_questionsheet(event,request.user)
    return render(request,'rsvp/event_detail.html',{'guest':guest,'event_id':event_id,'quizsheet':questionsheet, 'event':event})
    
@login_required
def profile(request):
    request.session.set_expiry(0)
    invite_events = Event.objects.filter(invite = request.user)
    owner_events = Event.objects.filter(owner = request.user)

    for event in owner_events:

        if request.POST.get(str(event.pk)):
            host = request.get_host()
            content = 'The Event <'+Event.objects.get(pk = event.pk).event_name + '> is deleted!'
            guest = event.guest.all()
            for g in guest:      
                text = 'The %s is cancelled!'%event.event_name
                html = u'Dear sir or madam:<br>The event is cancelled, please login and check!<a href = "http://{}">Click to Login<a>'.format(host)
                send_email(g.email,text,html)
                break
            Event.objects.filter(pk = event.pk).delete()
    owner_events = Event.objects.filter(owner = request.user)
    vendor_events = Event.objects.filter(vendor = request.user)
    guest_events = Event.objects.filter(guest = request.user)
    args = {'owner_events':owner_events, 'vendor_events':vendor_events, 'guest_events':guest_events, 'invite_events':invite_events}
    return render(request, 'rsvp/profile.html', args)


@login_required
def expire_question(request,event_id):
    try:
        event = Event.objects.get(pk = event_id)
    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    guest = event.guest.all();
    if request.method == "POST":
        q = Question.objects.filter(event_belong = event)
        for i in q:
            if request.POST.get(str(i.pk)):
                question = Question.objects.get(pk = i.pk)
                question.expired = True
                question.save()
                break  
    q = Question.objects.filter(event_belong = event)
    quizsheet = {}
    questionsheet = get_questionsheet(event,request.user)
    return render(request,'rsvp/expire_question.html',{'quizsheet':questionsheet,'event_id':event_id, 'guest':guest})
        
        
@login_required
def question_change(request,event_id,question_id ):
    q = get_object_or_404(Question,pk = question_id)
    event = get_object_or_404(Event,pk = event_id)
    if request.COOKIES.get('extra'):
        extra = int(request.COOKIES.get('extra'))
    else:
        extra = 0
    if request.method == "POST":
        host = request.get_host()
        vendor = AddVendorForm(request.POST or None, instance = event)
        vendor.fields["vendor"].queryset = event.vendor.all()
        question = QuestionForm(request.POST or None, initial={'name':q.name})
        if request.POST.get('sub'):
            choice = ChoiceForm(request.POST, extra = extra)
            if question.is_valid():
                q.name = question.cleaned_data['name']
                q.save()
            if vendor.is_valid():
                v = vendor.cleaned_data['vendor']
                for i in v:
                    q.vendor.add(i)
                q.save()
            if choice.is_valid():
                formal_choice = Choice.objects.filter(question = q)#.delete()
                for i in range(0,extra):
                    if request.POST['choice_%i'%i]:
                        if not formal_choice.filter(choice_text = request.POST['choice_%i'%i]):
                            c  = Choice(choice_text=request.POST['choice_%i'%i], question = q,votes = 0)
                            c.save()
                            
                        formal_choice=formal_choice.exclude(choice_text = request.POST['choice_%i'%i])
                for f in formal_choice:
                    print(f.choice_text)
                    text = 'Question change!%s!'%event.event_name
                    html = u'Dear sir or madam:<br>In the Question <b>{}</b>,your choice <b>{}</b> is delete,please login to change your answer!<br><a href = "http://{}">Click to Login<a>'.format(q.name,f.choice_text,host)
                    ans = Answer.objects.filter(answer_text = f.pk)
                    for a in ans:
                        send_email(a.user.email,text,html)
                    Choice.objects.filter(pk = f.pk).delete()
                    Answer.objects.filter(answer_text = f.pk).delete()
                print(formal_choice)
                #Choice.objects.filter(question = q).delete()
                if extra == 0:
                    q.multi = False
                    q.save()
            response = redirect('/rsvp/%s/event_detail'%event_id)
            response.delete_cookie('extra')
            return response
        if request.POST.get('add'):
            extra += 1
        if request.POST.get('del'):
            extra -= 1
        choice = ChoiceForm(request.POST or None, extra = extra)
    else:
        extra = 0
        vendor = AddVendorForm(request.POST or None)
        vendor.fields["vendor"].queryset = event.vendor.all()
        choice = ChoiceForm(request.POST or None, extra = extra)
        question = QuestionForm(initial={'name':q.name})
        if q.multi:
            c = Choice.objects.filter(question = q)
            extra = c.count()
            choice = ChoiceForm(request.POST or None, extra = extra)
            n = 0
            data = {}
            for i in c:
                data['choice_%i'%n] = i.choice_text
                n+=1
            choice.initial = data
    response = render(request,'rsvp/change.html',{'question':question,'vendor':vendor,'choice':choice})
    response.set_cookie('extra',extra)
    return response
    
    
@login_required
def answer_sheet(request, event_id, guest_id):
    event = get_object_or_404(Event, pk = event_id)
    guest = User.objects.get(pk = guest_id)
    answersheet = get_answersheet(event,request.user,guest,False)
    guest_answersheet = get_answersheet(event,request.user,guest,True)
    return render(request,'rsvp/answer_sheet.html',{'event_id':event_id,'answersheet':answersheet,'guestanswersheet':guest_answersheet,'guest':guest.username}) 
    
@login_required    
def view_event_detail(request, event_id):
    event = get_object_or_404(Event, pk = event_id)
    return render(request,'rsvp/view_event_detail.html',{'event':event}) 