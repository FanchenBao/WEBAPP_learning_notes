''' learning_notes views'''
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Topic, Entry
from .forms import TopicForm, EntryForm



def index(request):
    ''' homepage'''
    return render(request, 'learning_notes/index.html')

def topics(request):
    ''' main topics page, display all topics'''
    topics = []
    for topic in Topic.objects.order_by('date_added'):
        count = topic.entry_set.count()
        topics.append({'id':topic.id, 'text':topic.text, 'count':count})
    context = {'topics' : topics}
    return render(request, 'learning_notes/topics.html', context)


def topic(request, topic_id):
    ''' each individual topic page. Display all entries related to the topic'''
    topic = Topic.objects.get(pk = topic_id)
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic' : topic, 'entries' : entries}
    return render(request, 'learning_notes/topic.html', context)

@login_required
def new_topic(request):
    ''' Add a new topic
        display empty form or process user-submitted form
    '''
    topicAlreadyExist = False # flag
    existingTopic = None
    if request.method != 'POST':
        form = TopicForm() # provide empty form if the request is not a form submission
    else: # user submit the form
        form = TopicForm(data = request.POST)
        if form.is_valid(): # check for validity
            new_topic = form.save(commit = False)
            checkExistQuerySet = Topic.objects.filter(text__iexact = new_topic.text)
            if checkExistQuerySet.exists(): # check whether the new topic already exists (case insensitive match)
                topicAlreadyExist = True # use this flag to print warning msg in html template when duplicate topic is entered
                existingTopic = checkExistQuerySet[0]
            else:
                new_topic.save()
                return HttpResponseRedirect(reverse('learning_notes:topics'))
    context = {'form':form, 'topicAlreadyExist':topicAlreadyExist, 'existingTopic':existingTopic}
    return render(request, 'learning_notes/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    ''' Add a new entry under a certain topic
        display empty form or process user-submitted form
    '''
    topic = Topic.objects.get(id = topic_id)
    if request.method != 'POST':
        form = EntryForm() # provide empty form if the request is not a form submission
    else: # user submit the form
        form = EntryForm(data = request.POST)
        if form.is_valid(): # check for validity
            new_entry = form.save(commit = False)
            new_entry.topic = topic
            new_entry.owner = request.user
            new_entry.save()
            return HttpResponseRedirect(reverse('learning_notes:topic', args = [topic_id]))
    context = {'form' : form, 'topic':topic}
    return render(request, 'learning_notes/new_entry.html', context)

@login_required
def edit_entry(request, topic_id, entry_id):
    '''edit an entry'''
    topic = Topic.objects.get(id = topic_id)
    entry = Entry.objects.get(id = entry_id)
    if entry.owner != request.user:
        raise Http404
    if request.method != 'POST':
        form = EntryForm(instance = entry) # fill the form with pre-existing data
    else:
        form = EntryForm(instance = entry, data = request.POST) # fill with pre-existing data first, but then update the data based on request.POST
        if form.is_valid(): # check for validity
            form.save()
            return HttpResponseRedirect(reverse('learning_notes:topic', args = [topic_id]))
    context = {'form':form, 'topic':topic, 'entry':entry}
    return render(request, 'learning_notes/edit_entry.html', context)

# @login_required
# def delete_topic(request, topic_id):
#     ''' delete a topic, its entries will be deleted as well'''
#     if topic.owner != request.user:
#         raise Http404
#     topic = Topic.objects.get(id = topic_id)
#     topic.delete()
#     return HttpResponseRedirect(reverse('learning_notes:topics'))

@login_required
def delete_entry(request, topic_id, entry_id):
    ''' delete a topic, its entries will be deleted as well'''
    entry = Entry.objects.get(id = entry_id)
    if entry.owner != request.user:
        raise Http404
    entry.delete()
    return HttpResponseRedirect(reverse('learning_notes:topic', args = [topic_id]))

def archive_user_topics(request, user_id):
    ''' display all topics a user has posted under'''
    user = User.objects.get(id = user_id)

    # the most important line in this view. This is to retrieve a querySet of topics,
    # at least one of whose related entries has the same owner as the passed in user.
    # Since entry is included in topic, even though topic doesn't have a field named
    # entry, one can access entry via topic by topic.entry_set or put entry directly
    # in the filter argument. Double underscore is used inside filter to further retrieve
    # field of entry. This filtering creates a querySet topics which the user has participated in.
    # Read for reference https://docs.djangoproject.com/en/2.1/topics/db/examples/many_to_one/
    topics = []
    
    # the distinct() function is essential, because entry__owner = user basically is 
    # doing a JOIN. Yet, since I don't know an easy way to do LEFT JOIN, the resulting
    # QuersySet for topics contain duplicates (e.g. if a user publishes two entries under a specific topic,
    # then each entry's owner would match the user once, giving two total matches. Each
    # match returns one account of the specific topic, thus we would have two copies of
    # the same topic in the resulting QuerySet. The solution is to constrain the returned
    # QuerySet as unique by using the distinct() function.
    for topic in Topic.objects.filter(entry__owner = user).distinct():
        # count how many entries this particular user has created
        count = topic.entry_set.filter(owner = user).count()
        
        topics.append({'id':topic.id, 'text':topic.text, 'count':count})
    context = {'topics':topics, 'archive_user':user}
    return render(request, 'learning_notes/archive_user_topics.html', context)

def archive_user_entries(request, user_id, topic_id):
    ''' display all entries owned by the user under a specific topic'''
    user = User.objects.get(id = user_id)
    topic = Topic.objects.get(id = topic_id)
    entriesUnderTopic = topic.entry_set.all()
    entriesUderUser = user.entry_set.all()
    entries = entriesUderUser.intersection(entriesUnderTopic) # the entries belonging to the user that are also under the current topic
    context = {'entries':entries, 'archive_user':user, 'topic':topic}
    return render(request, 'learning_notes/archive_user_entries.html', context)




