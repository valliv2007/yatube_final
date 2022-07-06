from django.core.paginator import Paginator


def paginate_posts(request, post_list, amount_posts):
    paginator = Paginator(post_list, amount_posts)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
