--
-- Name: geneexpressionstudy; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneexpressionstudy FROM PUBLIC;
REVOKE ALL ON TABLE geneexpressionstudy FROM agrbrdf;
GRANT ALL ON TABLE geneexpressionstudy TO agrbrdf;
GRANT SELECT ON TABLE geneexpressionstudy TO gbs;


