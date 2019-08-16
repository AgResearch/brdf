--
-- Name: workflowstageob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE workflowstageob FROM PUBLIC;
REVOKE ALL ON TABLE workflowstageob FROM agrbrdf;
GRANT ALL ON TABLE workflowstageob TO agrbrdf;
GRANT SELECT ON TABLE workflowstageob TO gbs;


