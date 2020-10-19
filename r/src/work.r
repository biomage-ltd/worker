library(RestRserve)
library(pagoda2)

message("Launching R worker...")

app <- Application$new()

message("Loading R object....")

data <- readRDS("/data/r.rds")

message("Initializing handlers...")

app$add_post(
    path = "/DifferentialExpression",
    FUN = function(request, response) {
        response$set_body("up")
    }
)

app$add_get(
    path = "/health",
    FUN = function(request, response) {
        response$set_body("up")
    }
)

message("Starting....")


backend <- BackendRserve$new()
backend$start(app, http_port = 4000)