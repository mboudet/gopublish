import React, { Component } from 'react'
import axios from 'axios'
import { Badge, Button, Card, CardDeck, CardTitle, CardBody, CardHeader, CardText, Col, Form, FormGroup, Input, Label} from 'reactstrap'
import update from 'react-addons-update'
import { withRouter } from "react-router-dom";
import PropTypes from 'prop-types'
import Utils from '../classes/utils'
import { Link, Redirect } from 'react-router-dom'
import FilesTable from './filestable'


class Search extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
  }

  render () {
    return (
        <FilesTable config={this.props.config} files={this.props.location.state.results} />
    )
  }
}

Search.propTypes = {
  config: PropTypes.object,
  location: PropTypes.object
}

export default withRouter(Search)
