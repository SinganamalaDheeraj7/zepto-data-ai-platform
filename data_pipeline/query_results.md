## where
```sql
SELECT title, price_gbp FROM books WHERE in_stock=1 LIMIT 5
```
| title                                                               |   price_gbp |
|:--------------------------------------------------------------------|------------:|
| It's Only the Himalayas                                             |       45.17 |
| Full Moon over Noahâs Ark: An Odyssey to Mount Ararat and Beyond                                                                     |       49.43 |
| See America: A Celebration of Our National Parks & Treasured Sites  |       48.87 |
| Vagabonding: An Uncommon Guide to the Art of Long-Term World Travel |       36.94 |
| Under the Tuscan Sun                                                |       37.33 |

## order_limit
```sql
SELECT title, price_inr FROM books ORDER BY price_inr DESC LIMIT 10
```
| title                                                                  |   price_inr |
|:-----------------------------------------------------------------------|------------:|
| Boar Island (Anna Pigeon #19)                                          |     6275.14 |
| The No. 1 Ladies' Detective Agency (No. 1 Ladies' Detective Agency #1) |     6087.35 |
| A Year in Provence (Provence #1)                                       |     6000.84 |
| The Past Never Ends                                                    |     5960.75 |
| The Last Painting of Sara de Vos                                       |     5860.52 |
| A Flight of Arrows (The Pathfinders #2)                                |     5858.42 |
| Murder at the 42nd Street Library (Raymond Ambler #1)                  |     5734.98 |
| The Last Mile (Amos Decker #2)                                         |     5719.16 |
| 1st to Die (Women's Murder Club #1)                                    |     5694.89 |
| Tipping the Velvet                                                     |     5669.57 |

## distinct
```sql
SELECT DISTINCT rating FROM books ORDER BY rating
```
|   rating |
|---------:|
|        1 |
|        2 |
|        3 |
|        4 |
|        5 |

## between
```sql
SELECT title, rating FROM books WHERE rating BETWEEN 4 AND 5 LIMIT 10
```
| title                                                                    |   rating |
|:-------------------------------------------------------------------------|---------:|
| Full Moon over Noahâs Ark: An Odyssey to Mount Ararat and Beyond                                                                          |        4 |
| A Year in Provence (Provence #1)                                         |        4 |
| 1,000 Places to See Before You Die                                       |        5 |
| Sharp Objects                                                            |        4 |
| The Past Never Ends                                                      |        4 |
| The Murder of Roger Ackroyd (Hercule Poirot #4)                          |        4 |
| A Time of Torment (Charlie Parker #14)                                   |        5 |
| Murder at the 42nd Street Library (Raymond Ambler #1)                    |        4 |
| What Happened on Beale Street (Secrets of the South Mysteries #2)        |        5 |
| The Bachelor Girl's Guide to Murder (Herringford and Watts Mysteries #1) |        5 |

## join
```sql
SELECT c.category_name, b.title, b.rating, b.price_gbp FROM books b JOIN categories c ON b.category_id=c.category_id ORDER BY b.rating DESC, b.price_gbp DESC LIMIT 10
```
| category_name      | title                                                                    |   rating |   price_gbp |
|:-------------------|:-------------------------------------------------------------------------|---------:|------------:|
| Historical Fiction | A Flight of Arrows (The Pathfinders #2)                                  |        5 |       55.53 |
| Mystery            | The Bachelor Girl's Guide to Murder (Herringford and Watts Mysteries #1) |        5 |       52.3  |
| Mystery            | A Time of Torment (Charlie Parker #14)                                   |        5 |       48.35 |
| Historical Fiction | While You Were Mine                                                      |        5 |       41.32 |
| Historical Fiction | The Red Tent                                                             |        5 |       35.66 |
| Historical Fiction | Mrs. Houdini                                                             |        5 |       30.25 |
| Historical Fiction | The Passion of Dolssa                                                    |        5 |       28.32 |
| Travel             | 1,000 Places to See Before You Die                                       |        5 |       26.08 |
| Mystery            | What Happened on Beale Street (Secrets of the South Mysteries #2)        |        5 |       25.37 |
| Mystery            | The Silkworm (Cormoran Strike #2)                                        |        5 |       23.05 |

## pandas merge equivalent to join
| category_name      | title                                                                    |   rating |   price_gbp |
|:-------------------|:-------------------------------------------------------------------------|---------:|------------:|
| Historical Fiction | A Flight of Arrows (The Pathfinders #2)                                  |        5 |       55.53 |
| Mystery            | The Bachelor Girl's Guide to Murder (Herringford and Watts Mysteries #1) |        5 |       52.3  |
| Mystery            | A Time of Torment (Charlie Parker #14)                                   |        5 |       48.35 |
| Historical Fiction | While You Were Mine                                                      |        5 |       41.32 |
| Historical Fiction | The Red Tent                                                             |        5 |       35.66 |
| Historical Fiction | Mrs. Houdini                                                             |        5 |       30.25 |
| Historical Fiction | The Passion of Dolssa                                                    |        5 |       28.32 |
| Travel             | 1,000 Places to See Before You Die                                       |        5 |       26.08 |
| Mystery            | What Happened on Beale Street (Secrets of the South Mysteries #2)        |        5 |       25.37 |
| Mystery            | The Silkworm (Cormoran Strike #2)                                        |        5 |       23.05 |