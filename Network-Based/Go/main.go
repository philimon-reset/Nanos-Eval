package main

import (
	"fmt"
	"net/http"
	"os"
)

func main() {
	// Default port
	port := "8080"

	// Check if a port was provided as the first argument
	if len(os.Args) > 1 {
		port = os.Args[1]
	}

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
// 		fmt.Printf("Received request: %s %s from %s.\n", r.Method, r.URL.Path, r.RemoteAddr)
		fmt.Fprintf(w, "Welcome to my website!")
	})

	fs := http.FileServer(http.Dir("static/"))
	http.Handle("/static/", http.StripPrefix("/static/", fs))

	addr := fmt.Sprintf(":%s", port)
	fmt.Printf("Starting server on port %s...", port)

	if err := http.ListenAndServe(addr, nil); err != nil {
		fmt.Printf("Server failed to start: %v", err)
	}
}
