from fastapi import FastAPI, status, Query, Path, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from storage import storage
from schemas import NewTour, SavedTour, TourPrice,  DeletedTour

app = FastAPI(
    debug=True,
    title='tourist_agency'
)


@app.get('/', include_in_schema=False)
@app.post('/', include_in_schema=False)
def index(request: Request, q: str = Form(default='')):
#     tours = storage.get_tours(limit=40, q=q)
#     context = {
#         'request': request,
#         'page_title': 'the best agency',
#         'tours': tours
#     }
#     return context
    return 'hello'

@app.post('/api/tour/', description="create tour", status_code=status.HTTP_201_CREATED, tags=['Tours'])
def add_product(new_tour: NewTour) -> SavedTour:
    saved_tour = storage.create_tour(new_tour)
    return saved_tour


@app.get('/api/tour/{tour_id}/', description='get tour', status_code=status.HTTP_200_OK, tags=['Tours'])
def get_tour(tour_id: int = Path(ge=1, description='tour id')) -> SavedTour:
    result = storage.get_tour(tour_id)
    return result


@app.get('/api/tour/', description='get tours', status_code=status.HTTP_200_OK, tags=['Tours'])
def get_tours(limit: int = Query(default=10, description='no more than tours'), q: str = ''):
    result = storage.get_tours(limit=limit, q=q)
    return result


@app.patch('/api/tour/{tour_id}/', description='update price', status_code=status.HTTP_200_OK, tags=['Tours'])
def update_tour_price(new_price: float, tour_id: int = Path(ge=1, description='tour_id')) -> SavedTour:
    result = storage.update_tour_price(_id=tour_id, new_price=new_price)
    return result


@app.delete('/api/tour/{tour_id}/', description='delete_tour', status_code=status.HTTP_200_OK, tags=['Tours'])
def delete_tour(tour_id: int = Path(ge=1, description='tour_id')) -> DeletedTour:
    storage.delete_tour(_id=tour_id)
    return DeletedTour(id=tour_id)
