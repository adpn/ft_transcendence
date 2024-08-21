from django.contrib.auth import login, logout, get_user_model
from django.http import JsonResponse, HttpResponse
from django.db.utils import IntegrityError
# from django.db import models

import json
from uuid import uuid4
from http import client
import os
