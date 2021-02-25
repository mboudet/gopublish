import React, { Component, createContext } from 'react'
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom'
import axios from 'axios'

import Home from './routes/home'
import File from './routes/file'

import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css'
import 'bootstrap/dist/css/bootstrap.min.css'

export default class Routes extends Component {

  constructor (props) {
    super(props)
    this.state = {
      config: {
        proxyPath: document.getElementById('proxy_path').getAttribute('proxy_path'),
      }
    }
    this.cancelRequest
  }

  render () {

    let redirectRoot

    if (document.getElementById('redirect').getAttribute('redirect') == "/") {
      redirectRoot = <Redirect to="/" />
    }

    return (
      <Router basename={this.state.config.proxyPath}>
        <div>
          {redirectRoot}
          <Switch>
            <Route path="/" exact component={() => (<Home config={this.state.config} />)} />
            <Route path="/files/:uri" exact component={() => (<File config={this.state.config} />)} />
          </Switch>
          <br />
          <br />
        </div>
      </Router>
    )
  }
}
