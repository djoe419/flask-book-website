from typing import List

from flask import Blueprint, render_template, url_for, session, redirect
import library.authentication.services as authentication_services
import library.books.services as book_services
from library.authentication.authentication import login_required
from library.authentication.services import get_user_from_cookie
import library.adapters.repository as repo
from library.books.book import BookAndListForm
from library.domain.model import User, Review
from library.user.service import user_to_dict
from utils import log

user_blueprint = Blueprint(
    'user_bp', __name__, url_prefix='/user'
)

NUMBER_OF_RECENT_REVIEWS = 4


def get_recent_reviews(user: User):
    results: List[dict] = []

    reviews = sorted(user.reviews, key=lambda x: x.timestamp, reverse=True)
    reviews = reviews[:NUMBER_OF_RECENT_REVIEWS] if len(reviews) > NUMBER_OF_RECENT_REVIEWS else reviews
    results = [{
        'book': book_services.book_to_dict(review.book),
        'review': book_services.review_to_dict(review),
        'authors': ', '.join(map(lambda a: a.full_name, review.book.authors))
    } for review in reviews]
    return results


@user_blueprint.route('/me', methods=['GET'])
@login_required
def get_profile():
    user = get_user_from_cookie(repo.repo_instance)
    if user is None:
        return redirect(url_for('home_bp.error'))

    recent_reviews = get_recent_reviews(user)
    shelve_dict = book_services.shelve_to_dict(user.shelve)
    form = BookAndListForm()

    return render_template(
        'user/profile_page.html',
        recent_reviews=recent_reviews,
        user=user_to_dict(user),
        shelve=shelve_dict,
        form=form,
        delete_url=url_for('book_bp.process_delete_list'),
        public_url=url_for('book_bp.change_is_public'),
    )
