from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Case, When, Value, IntegerField
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .models import Category, Item


def search(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')

    items = Item.objects.select_related('category').all()

    if query:
        items = items.filter(Q(code__icontains=query) | Q(name__icontains=query))

    if category_id:
        items = items.filter(category_id=category_id)

    categories = Category.objects.all()

    context = {
        'items': items,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'total_count': Item.objects.count(),
    }
    return render(request, 'catalog/search.html', context)


def suggest(request):
    """JSON endpoint for the live autocomplete dropdown on the search box."""
    query = request.GET.get('q', '').strip()
    if len(query) < 1:
        return JsonResponse({'results': []})

    items = (
        Item.objects.select_related('category')
        .filter(Q(code__icontains=query) | Q(name__icontains=query))
        # exact/starts-with matches on code or name float to the top
        .annotate(
            rank=Case(
                When(code__iexact=query, then=Value(0)),
                When(code__istartswith=query, then=Value(1)),
                When(name__istartswith=query, then=Value(2)),
                default=Value(3),
                output_field=IntegerField(),
            )
        )
        .order_by('rank', 'name')[:8]
    )

    results = [
        {
            'code': item.code,
            'name': item.name,
            'category': item.category.name if item.category else '',
            'wholesale': f'{item.wholesale_price:.2f}',
            'retail': f'{item.retail_price:.2f}',
        }
        for item in items
    ]
    return JsonResponse({'results': results})


def customer_lookup(request):
    """
    JSON endpoint for the price display screen (shown after a barcode scan).
    Returns both wholesale and retail — this is a wholesale shop, so
    wholesale is the primary price shown; retail is available via a
    toggle on the same screen.
    """
    barcode = request.GET.get('barcode', '').strip()
    if not barcode:
        return JsonResponse({'found': False})

    try:
        item = Item.objects.get(barcode=barcode)
    except Item.DoesNotExist:
        return JsonResponse({'found': False})

    return JsonResponse({
        'found': True,
        'item_no': item.code,
        'name': item.name,
        'wholesale': f'{item.wholesale_price:.2f}',
        'retail': f'{item.retail_price:.2f}',
    })


@login_required
def bulk_add(request):
    result_message = None

    if request.method == 'POST':
        raw_text = request.POST.get('bulk_text', '')
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        added = 0
        skipped = 0

        for line in lines:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 5:
                skipped += 1
                continue
            code, name, category_name, wholesale, retail = parts[:5]
            barcode = parts[5] if len(parts) > 5 and parts[5] else None
            try:
                wholesale_price = float(wholesale)
                retail_price = float(retail)
            except ValueError:
                skipped += 1
                continue

            category = None
            if category_name:
                category, _ = Category.objects.get_or_create(name=category_name)

            Item.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'category': category,
                    'wholesale_price': wholesale_price,
                    'retail_price': retail_price,
                    'barcode': barcode,
                },
            )
            added += 1

        messages.success(request, f'Added or updated {added} items. Skipped {skipped} invalid lines.')
        return redirect('bulk_add')

    return render(request, 'catalog/bulk_add.html', {'result_message': result_message})
