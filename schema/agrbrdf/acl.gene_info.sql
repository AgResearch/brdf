--
-- Name: gene_info; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE gene_info FROM PUBLIC;
REVOKE ALL ON TABLE gene_info FROM agrbrdf;
GRANT ALL ON TABLE gene_info TO agrbrdf;
GRANT SELECT ON TABLE gene_info TO gbs;


