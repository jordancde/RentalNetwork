from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path, include
from django.contrib import admin
import oauth2_provider.views as oauth2_views
from rental import views
from backend import settings
admin.autodiscover()

# OAuth2 provider endpoints
oauth2_endpoint_views = [
    url(r'^authorize/$', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^token/$', oauth2_views.TokenView.as_view(), name="token"),
    url(r'^revoke-token/$', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

if settings.DEBUG:
    # OAuth2 Application Management endpoints
    oauth2_endpoint_views += [
        url(r'^applications/$', oauth2_views.ApplicationList.as_view(), name="list"),
        url(r'^applications/register/$', oauth2_views.ApplicationRegistration.as_view(), name="register"),
        url(r'^applications/(?P<pk>\d+)/$', oauth2_views.ApplicationDetail.as_view(), name="detail"),
        url(r'^applications/(?P<pk>\d+)/delete/$', oauth2_views.ApplicationDelete.as_view(), name="delete"),
        url(r'^applications/(?P<pk>\d+)/update/$', oauth2_views.ApplicationUpdate.as_view(), name="update"),
    ]

    # OAuth2 Token Management endpoints
    oauth2_endpoint_views += [
        url(r'^authorized-tokens/$', oauth2_views.AuthorizedTokensListView.as_view(), name="authorized-token-list"),
        url(r'^authorized-tokens/(?P<pk>\d+)/delete/$', oauth2_views.AuthorizedTokenDeleteView.as_view(),
            name="authorized-token-delete"),
    ]

urlpatterns = [
    path('users/', views.UserList.as_view()),
    path('users/<pk>/', views.UserDetails.as_view()),
    path('groups/', views.GroupList.as_view()),
    url(r'^api/token/', obtain_auth_token, name='api-token'),
    url(r"^admin/", admin.site.urls),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),

    url(r"^renters/$", views.RenterList,name="renter-list"),
    url(r"^renters/(?P<pk>\d+)/$", views.RenterDetails,name="renter-detail"),

    url(r"^landlords/$", views.LandlordList,name="landlord-list"),
    url(r"^landlords/(?P<pk>\d+)/$", views.LandlordDetails,name="landlord-detail"),

    url(r"^events/$", views.Events,name="event-list"),
    url(r"^events/(?P<pk>\d+)/$", views.EventDetails.as_view(),name="event-detail"),

    url(r"^listings/$", views.ListingsView,name="listing-list"),
    url(r"^listings/(?P<pk>\d+)/$", views.ListingDetails.as_view(),name="listing-detail"),

    url(r"^requests/$", views.Requests,name="request-list"),
    url(r"^requests/open", views.OpenRequests,name="open-requests"),
    url(r"^requests/accepted", views.AcceptedRequests,name="accepted-requests"),
    url(r"^requests/(?P<pk>\d+)/$", views.RequestDetails.as_view(),name="request-detail"),
    
    #url(r'^asset/', views.AssetDetail),
    
]
