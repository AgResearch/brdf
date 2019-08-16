--
-- Name: workflowlink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE workflowlink FROM PUBLIC;
REVOKE ALL ON TABLE workflowlink FROM agrbrdf;
GRANT ALL ON TABLE workflowlink TO agrbrdf;
GRANT SELECT ON TABLE workflowlink TO gbs;


