--
-- Name: geneproductlink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneproductlink FROM PUBLIC;
REVOKE ALL ON TABLE geneproductlink FROM agrbrdf;
GRANT ALL ON TABLE geneproductlink TO agrbrdf;
GRANT SELECT ON TABLE geneproductlink TO gbs;


