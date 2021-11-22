# Configure blueprint.
from math import floor, ceil

from better_profanity import profanity
from flask import Blueprint, request, render_template, abort, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, InputRequired

from utils import str_to_int_list, log
from .services import *
import library.books.services as book_service
import library.adapters.repository as repo
import library.authentication.services as auth_service
from ..authentication.authentication import login_required

book_blueprint = Blueprint('book_bp', __name__)

DEFAULT_NUMBER_OF_BOOKS_PER_PAGE = 6
NEW_LIST_OPTION_VALUE = -1


@book_blueprint.route('/book', methods=['GET', 'POST'])
def single_book():
    book_id = request.args.get('id')
    # if tried to add a new list with empty name
    try:
        error_msgs = request.args.get('error').strip().split(',')
        for msg in error_msgs:
            flash(msg)
    except (NameError, AttributeError):
        pass

    book = None
    reviews = []
    try:
        book_id = int(book_id)
        book = get_book(book_id, repo.repo_instance)
        reviews = get_reviews_for_book(book_id, repo.repo_instance)
    except NonExistentBookException as e:
        pass
    except ValueError as e:
        pass

    user = auth_service.get_user_from_cookie(repo.repo_instance)
    should_have_form = False
    form = None
    handler_url = url_for('book_bp.process_shelve_changes')
    if user:
        should_have_form = True
        reading_list_name = [(reading_list.uid, reading_list.name) for reading_list in user.shelve.reading_lists]

        form = ShelveChangeForm()
        form.name_list.choices = [*reading_list_name, (NEW_LIST_OPTION_VALUE, 'New reading list')]
        form.book_id.data = book_id
        form.method.data = 'add'
        form.original_url.data = request.url

    return render_template(
        'book/book.html',
        book=book,
        reviews=reviews,
        should_have_form=should_have_form,
        form=form,
        handler_url=handler_url,
    )


@book_blueprint.route('/book/review', methods=['GET', 'POST'])
@login_required
def add_review():
    form = ReviewForm()
    if form.validate_on_submit():
        user_name = session['user_name']
        book_service.add_review(int(form.book_id.data), form.rating.data, form.review.data, user_name,
                                repo.repo_instance)
        return redirect(url_for('book_bp.single_book', id=form.book_id.data))

    if request.method == 'GET':
        book_id = int(request.args.get('id'))
        form.book_id.data = book_id
    else:
        book_id = int(form.book_id.data)
    book = get_book(book_id, repo.repo_instance)

    return render_template(
        'book/comment.html',
        handleurl=url_for('book_bp.add_review'),
        form=form,
        book=book,
        id=book_id
    )


@book_blueprint.route('/search_books_result', methods=['GET'])
def display_book_list():
    # get args
    book_ids = request.args.get('book_ids', [], str_to_int_list)
    current_page = request.args.get('page', 1, int)
    books_per_page = request.args.get('bpp', DEFAULT_NUMBER_OF_BOOKS_PER_PAGE, int)

    # paginate
    id_string = ','.join([str(id_) for id_ in book_ids])
    paginated_ids, number_of_pages, display_paging, shadow_first, shadow_last = paginate(book_ids, books_per_page,
                                                                                         current_page)
    should_disable_last = "disabled" if shadow_last else ""
    should_disable_first = "disabled" if shadow_first else ""

    # books
    books = get_books(paginated_ids, repo.repo_instance)

    return render_template(
        'book/book_list.html',
        books=books,
        total_results=len(book_ids),
        display_paging=display_paging,
        number_of_pages=number_of_pages,
        id_string=id_string,
        current_page=current_page,
        books_per_page=books_per_page,
        should_disable_last=should_disable_last,
        should_disable_first=should_disable_first
    )


@book_blueprint.route('/reading_list', methods=['GET'])
def display_reading_list():
    # get args
    reading_list_id = request.args.get('id', -1, int)
    current_page = request.args.get('page', 1, int)
    books_per_page = request.args.get('bpp', DEFAULT_NUMBER_OF_BOOKS_PER_PAGE, int)
    user = auth_service.get_user_from_cookie(repo.repo_instance)
    reading_list = repo.repo_instance.get_reading_list_by_id(reading_list_id)

    if not can_view_reading_list(reading_list, user):
        return redirect('home_bp.error')

    # paginate
    paginated_books, number_of_pages, display_paging, shadow_first, shadow_last = \
        paginate(reading_list.books, books_per_page, current_page)

    paginated_books = [book_to_dict(paginated_book) for paginated_book in paginated_books]

    should_disable_last = "disabled" if shadow_last else ""
    should_disable_first = "disabled" if shadow_first else ""

    form = None
    can_modify = can_modify_reading_list(reading_list, user)
    if can_modify:
        form = BookAndListForm()
        form.reading_list_id.data = reading_list.uid
    else:
    #     guest
        user = reading_list.shelve.user.user_name

    return render_template(
        'book/reading_list.html',
        list=reading_list,
        books=paginated_books,
        total_results=len(reading_list.books),
        display_paging=display_paging,
        number_of_pages=number_of_pages,
        id=reading_list_id,
        current_page=current_page,
        books_per_page=books_per_page,
        should_disable_last=should_disable_last,
        should_disable_first=should_disable_first,
        can_modify=can_modify,
        form=form,
        handler_url=url_for('book_bp.process_delete_book'),
        user=user
    )


@book_blueprint.route('/process-shelve', methods=['POST'])
@login_required
def process_shelve_changes():
    """add or remove a book from a list"""
    form = ShelveChangeForm()
    user = auth_service.get_user_from_cookie(repo.repo_instance)
    reading_lists = [(reading_list.uid, reading_list.name) for reading_list in user.shelve.reading_lists]
    choices = [(NEW_LIST_OPTION_VALUE, 'name'), *reading_lists]
    form.name_list.choices = choices
    shelve = user.shelve
    if form.validate_on_submit():
        # get reading list
        if form.name_list.data == NEW_LIST_OPTION_VALUE:
            name = form.new_name.data
            reading_list = make_new_reading_list(name, shelve, repo.repo_instance)
        else:
            reading_list = repo.repo_instance.get_reading_list_by_id(form.name_list.data)
            if reading_list is None:
                return redirect(url_for('home_bp.error'))
        # get book
        book = repo.repo_instance.get_book(int(form.book_id.data))
        if form.method.data == 'add':
            reading_list.add_book(book)
        elif form.method.data == 'del':
            reading_list.remove_book(book)
        repo.repo_instance.commit()
        return redirect(url_for('book_bp.display_reading_list', id=reading_list.uid))
        # return redirect(form.original_url.data)
    error_msg = ','.join(form.new_name.errors)
    if '?' in form.original_url.data:
        format_str = "%s&error=%s"
    else:
        format_str = "%s?error=%s"
    return redirect(format_str % (form.original_url.data, error_msg))


@book_blueprint.route('/process_search_book', methods=['GET'])
def process_search_book():
    search_method = request.args.get('method')
    book_ids = []
    if search_method == 'Title':
        title = request.args.get('param')
        book_ids = get_book_ids_by_title(title, repo.repo_instance)
    elif search_method == 'Author':
        author = request.args.get('param')
        book_ids = get_book_ids_by_author_name(author, repo.repo_instance)
    elif search_method == 'Publisher':
        publisher = request.args.get('param')
        book_ids = get_book_ids_by_publisher_name(publisher, repo.repo_instance)
    elif search_method == 'Release Year':
        yr = request.args.get('param', -1, int)
        book_ids = get_book_ids_by_year(yr, repo.repo_instance, after_year=False)
    elif search_method == 'Year since':
        yr = request.args.get('param', -1, int)
        book_ids = get_book_ids_by_year(yr, repo.repo_instance, after_year=True)
    else:
        abort(404)
    id_string = ','.join([str(id_) for id_ in book_ids])
    return redirect(url_for('book_bp.display_book_list', book_ids=id_string, page=1))


@book_blueprint.route('/process_book_delete', methods=['POST'])
def process_delete_book():
    form = BookAndListForm()
    if form.validate_on_submit():
        book_id = int(form.book_id.data)
        book = repo.repo_instance.get_book(book_id)
        list_id = int(form.reading_list_id.data)
        reading_list = repo.repo_instance.get_reading_list_by_id(list_id)
        reading_list.remove_book(book)
        repo.repo_instance.commit()
        return redirect(url_for('book_bp.display_reading_list', id=list_id))
    return redirect(url_for('home_bp.error'))


@book_blueprint.route('/process_list_delete', methods=['POST'])
def process_delete_list():
    form = BookAndListForm()
    if form.validate_on_submit():
        list_id = int(form.reading_list_id.data)
        remove_reading_list(list_id, repo.repo_instance)
        return redirect(url_for('user_bp.get_profile', id=list_id))
    return redirect(url_for('home_bp.error'))


@book_blueprint.route('/process_change_is_public', methods=['POST'])
def change_is_public():
    form = BookAndListForm()
    if form.validate_on_submit():
        list_id = int(form.reading_list_id.data)
        list_ = repo.repo_instance.get_reading_list_by_id(list_id)
        list_.is_public = not list_.is_public
        repo.repo_instance.commit()
        return redirect(url_for('user_bp.get_profile'))
    return redirect(url_for('home_bp.error'))


def paginate(item_list: List, item_per_page: int, current_page: int) -> (List, int):
    """get pagination information of the given list
    :return items : items to display
    :return total_num_of_pages
    :return should_display: whether there is more than 1 page
    :return shadow_first, shadow_last: whether first page or last page is reached"""
    items = item_list[(current_page - 1) * item_per_page: current_page * item_per_page]
    total_num_of_pages = ceil(len(item_list) / item_per_page)
    should_display = total_num_of_pages > 1
    shadow_first = current_page == 1
    shadow_last = current_page == total_num_of_pages

    return items, total_num_of_pages, should_display, shadow_first, shadow_last


class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)


class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")], coerce=int)
    review = TextAreaField('Review', [
        DataRequired(),
        Length(min=8, message='Your comment is too short'),
        ProfanityFree(message='Your comment must not contain profanity')])
    book_id = HiddenField("Book id")
    submit = SubmitField('Submit')


class BookAndListForm(FlaskForm):
    book_id = HiddenField("Book id")
    reading_list_id = HiddenField("List id")


class ShelveChangeForm(FlaskForm):
    name_list = SelectField('Reading List', coerce=int, validators=[InputRequired()])
    new_name = TextAreaField('Name for new list')
    book_id = HiddenField("Book id")
    original_url = HiddenField("Original URL")
    submit = SubmitField('Submit')
    method = HiddenField("Add/Delete")

    def validate_new_name(form, new_name):
        if form.name_list.data == NEW_LIST_OPTION_VALUE:
            if new_name.data.strip() == "":
                raise ValidationError("Please supply the name of new list")
